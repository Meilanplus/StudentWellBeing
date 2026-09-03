from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.intervention import Referral, ReferralReport
from app.schemas.risk import ReferralDocument, ReferralDocumentRequest, ReferralReportOut, ReferralReportSaveRequest
from app.agents.referral_agent import ReferralAgent
from app.services.i18n_lookup import get_language_display_name
from app.services.report_translator import translate_report_data
from app.permissions import require_task
from app.constants import TASK_INVOKE_AGENT3_REFERRAL

router = APIRouter(prefix="/referrals", tags=["Referral Documents"])


def _get_student_or_404(student_id: str, db: Session) -> Student:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return student


@router.post("/generate", response_model=ReferralDocument)
def generate_referral(
    req: ReferralDocumentRequest,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT3_REFERRAL)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(req.student_id, db)
    agent = ReferralAgent(db)
    document = agent.generate(
        student,
        referral_type=req.referral_type,
        referral_to=req.referral_to,
        prepared_by=req.prepared_by or requester.name,
        additional_notes=req.additional_notes or "",
        language=get_language_display_name(req.language, db),
    )

    record = Referral(
        student_id=student.id,
        referral_date=date.today(),
        referral_type=req.referral_type,
        referral_to=req.referral_to,
        reason=document.supporting_summary,
        document_content=document.letter_content,
        supporting_data=document.model_dump(),
        prepared_by=req.prepared_by or requester.name,
    )
    db.add(record)
    db.commit()
    return document


@router.post("/{student_id}/reports", response_model=ReferralReportOut)
def save_referral_report(
    student_id: str,
    payload: ReferralReportSaveRequest,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT3_REFERRAL)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    doc = payload.document
    # Deduplicated by (student, referral_type, referral_to) rather than by
    # date — a referral to the same professional doesn't need regenerating
    # just because a day has passed.
    existing = (
        db.query(ReferralReport)
        .filter(
            ReferralReport.student_id == student.id,
            ReferralReport.referral_type == doc.referral_type,
            ReferralReport.referral_to == doc.referral_to,
        )
        .order_by(ReferralReport.created_at.desc())
        .first()
    )
    if existing:
        return existing

    record = ReferralReport(
        student_id=student.id,
        referral_type=doc.referral_type,
        referral_to=doc.referral_to,
        additional_notes=payload.additional_notes or None,
        report_data=doc.model_dump(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{student_id}/reports", response_model=list[ReferralReportOut])
def list_referral_reports(
    student_id: str,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT3_REFERRAL)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    return (
        db.query(ReferralReport)
        .filter(ReferralReport.student_id == student.id)
        .order_by(ReferralReport.created_at.desc())
        .all()
    )


@router.post("/reports/{report_id}/translate")
def translate_saved_referral_report(
    report_id: int,
    language: str,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT3_REFERRAL)),
    db: Session = Depends(get_db),
):
    """Cached translation for a saved referral letter — see
    translate_saved_risk_report (app/api/risk.py) for the rationale."""
    record = db.query(ReferralReport).filter(ReferralReport.id == report_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Referral report not found.")
    if language == "ms":
        return record.report_data
    cached = record.translations.get(language)
    if cached is not None:
        return cached

    translated = translate_report_data(record.report_data, language)
    record.translations = {**record.translations, language: translated}
    db.commit()
    return translated


@router.get("/{student_id}")
def list_referrals(
    student_id: str,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT3_REFERRAL)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    referrals = db.query(Referral).filter(Referral.student_id == student.id).order_by(Referral.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "referral_date": r.referral_date.isoformat(),
            "referral_type": r.referral_type,
            "referral_to": r.referral_to,
            "status": r.status,
            "prepared_by": r.prepared_by,
        }
        for r in referrals
    ]


@router.patch("/{referral_id}/acknowledge")
def acknowledge_referral(
    referral_id: int,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT3_REFERRAL)),
    db: Session = Depends(get_db),
):
    referral = db.query(Referral).filter(Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found.")
    referral.status = "acknowledged"
    db.commit()
    return {"message": "Referral acknowledged.", "referral_id": referral_id}
