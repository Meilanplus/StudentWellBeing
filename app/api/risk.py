from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
import io

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.student import Student
from app.models.intervention import Intervention, RiskReport, InterventionReport
from app.schemas.risk import (
    RiskAssessment,
    InterventionRecommendation,
    RiskReportOut,
    InterventionReportOut,
    TranslateReportRequest,
)
from app.services.risk_calculator import compute_pre_screen_score, compute_pre_screen_detail
from app.services.i18n_lookup import get_translation, get_language_display_name
from app.services.intervention_report import generate_intervention_docx
from app.services.report_translator import translate_report_data
from app.agents.risk_detection_agent import RiskDetectionAgent
from app.agents.intervention_agent import InterventionAgent
from app.permissions import require_task
from app.constants import TASK_INVOKE_AGENT1_RISK, TASK_INVOKE_AGENT2_INTERVENTION

router = APIRouter(prefix="/risk", tags=["Risk & Intervention"])

PRE_SCREEN_SKIP_THRESHOLD = 15


def _get_student_or_404(student_id: str, db: Session) -> Student:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return student


@router.get("/{student_id}/assess", response_model=RiskAssessment)
def assess_risk(
    student_id: str,
    language: str = "ms",
    requester: User = Depends(require_task(TASK_INVOKE_AGENT1_RISK)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    score, flags = compute_pre_screen_score(student.id, db)

    if score < PRE_SCREEN_SKIP_THRESHOLD and not flags:
        return RiskAssessment(
            student_id=student.student_id,
            student_name=student.full_name,
            risk_level="Low Risk",
            risk_score=score,
            risk_factors=[],
            summary=get_translation("prescreen.low_risk_summary", language, db, default="No significant risk indicators found."),
            recommended_actions=[get_translation("prescreen.low_risk_action", language, db, default="Continue routine monitoring.")],
        )

    agent = RiskDetectionAgent(db)
    return agent.analyze(student, language=get_language_display_name(language, db))


@router.post("/{student_id}/reports", response_model=RiskReportOut)
def save_risk_report(
    student_id: str,
    payload: RiskAssessment,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT1_RISK)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    # One report per student per day — if today's already saved, return it
    # instead of writing a duplicate (enforced here, not just client-side,
    # so concurrent clicks/tabs can't race past the check).
    existing = (
        db.query(RiskReport)
        .filter(RiskReport.student_id == student.id, func.date(RiskReport.created_at) == date.today())
        .order_by(RiskReport.created_at.desc())
        .first()
    )
    if existing:
        return existing

    record = RiskReport(
        student_id=student.id,
        risk_level=payload.risk_level,
        risk_score=payload.risk_score,
        report_data=payload.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{student_id}/reports", response_model=list[RiskReportOut])
def list_risk_reports(
    student_id: str,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT1_RISK)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    return (
        db.query(RiskReport)
        .filter(RiskReport.student_id == student.id)
        .order_by(RiskReport.created_at.desc())
        .all()
    )


@router.post("/reports/translate")
def translate_report(
    payload: TranslateReportRequest,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT1_RISK)),
):
    return translate_report_data(payload.report, payload.target_language)


@router.get("/{student_id}/intervene", response_model=InterventionRecommendation)
def intervene(
    student_id: str,
    school_name: str = "",
    prepared_by: str = "",
    language: str = "ms",
    requester: User = Depends(require_task(TASK_INVOKE_AGENT2_INTERVENTION)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    lang_name = get_language_display_name(language, db)

    # Reuse the student's last saved risk assessment instead of re-running
    # Agent 1 if one already exists (any date) — Agent 1 only runs fresh for
    # students with no saved report at all.
    existing_risk_report = (
        db.query(RiskReport)
        .filter(RiskReport.student_id == student.id)
        .order_by(RiskReport.created_at.desc())
        .first()
    )
    if existing_risk_report:
        risk_assessment = RiskAssessment(**existing_risk_report.report_data)
    else:
        risk_agent = RiskDetectionAgent(db)
        risk_assessment = risk_agent.analyze(student, language=lang_name)

    intervention_agent = InterventionAgent(db)
    plan = intervention_agent.recommend(
        student,
        risk_assessment,
        school_name=school_name,
        prepared_by=prepared_by or requester.name,
        language=lang_name,
    )

    record = Intervention(
        student_id=student.id,
        risk_level=risk_assessment.risk_level,
        intervention_type="ai_comprehensive",
        description=plan.counselor_recommendation,
        start_date=date.today(),
        ai_recommendations=plan.model_dump(),
        assigned_to=prepared_by or requester.name,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    plan.intervention_id = record.id
    return plan


@router.post("/{student_id}/intervention-reports", response_model=InterventionReportOut)
def save_intervention_report(
    student_id: str,
    payload: InterventionRecommendation,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT2_INTERVENTION)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    existing = (
        db.query(InterventionReport)
        .filter(InterventionReport.student_id == student.id, func.date(InterventionReport.created_at) == date.today())
        .order_by(InterventionReport.created_at.desc())
        .first()
    )
    if existing:
        return existing

    record = InterventionReport(
        student_id=student.id,
        risk_level=payload.risk_level,
        report_data=payload.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{student_id}/intervention-reports", response_model=list[InterventionReportOut])
def list_intervention_reports(
    student_id: str,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT2_INTERVENTION)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    return (
        db.query(InterventionReport)
        .filter(InterventionReport.student_id == student.id)
        .order_by(InterventionReport.created_at.desc())
        .all()
    )


@router.get("/interventions/{intervention_id}/report")
def download_intervention_report(
    intervention_id: int,
    language: str = "ms",
    requester: User = Depends(require_task(TASK_INVOKE_AGENT2_INTERVENTION)),
    db: Session = Depends(get_db),
):
    record = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not record or not record.ai_recommendations:
        raise HTTPException(status_code=404, detail="Intervention plan not found.")

    plan = InterventionRecommendation(**record.ai_recommendations)
    docx_bytes = generate_intervention_docx(plan, language, db)
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="intervention_plan_{plan.student_id}.docx"'},
    )


@router.get("/{student_id}/prescreen")
def pre_screen(
    student_id: str,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT1_RISK)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    detail = compute_pre_screen_detail(student.id, db)
    score = detail["score"]
    if score >= settings.high_risk_threshold:
        level = "High Risk"
    elif score >= settings.moderate_risk_threshold:
        level = "Moderate Risk"
    else:
        level = "Low Risk"
    return {
        "student_id": student.student_id,
        "score": score,
        "level": level,
        "flags": detail["flags"],
        "breakdown": detail["breakdown"],
    }
