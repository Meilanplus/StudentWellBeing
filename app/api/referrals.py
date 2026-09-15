from datetime import date
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.intervention import Referral, ReferralReport
from app.schemas.risk import ReferralDocument, ReferralDocumentRequest, ReferralReportOut, ReferralReportSaveRequest
from app.agents.referral_agent import ReferralAgent
from app.services.i18n_lookup import get_language_display_name
from app.services.report_translator import translate_report_data, ensure_all_translations
from app.services.referral_report import generate_referral_docx
from app.services.dashboard_cache import invalidate_dashboard_cache
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
    invalidate_dashboard_cache(db)  # new Referral changes dashboard KPIs
    return document


@router.post("/{student_id}/reports", response_model=ReferralReportOut)
def save_referral_report(
    student_id: str,
    payload: ReferralReportSaveRequest,
    ui_language: str = "ms",
    requester: User = Depends(require_task(TASK_INVOKE_AGENT3_REFERRAL)),
    db: Session = Depends(get_db),
):
    """See save_risk_report() (app/api/risk.py) — same eager-translation-on-
    save behavior via ensure_all_translations()."""
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
        ensure_all_translations(existing, db, ui_language)
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
    ensure_all_translations(record, db, ui_language)
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


@router.get("/reports/{report_id}/report")
def download_referral_report(
    report_id: int,
    language: str = "ms",
    requester: User = Depends(require_task(TASK_INVOKE_AGENT3_REFERRAL)),
    db: Session = Depends(get_db),
):
    record = db.query(ReferralReport).filter(ReferralReport.id == report_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Referral report not found.")

    if language == "ms":
        data = record.report_data
    else:
        data = record.translations.get(language)
        if data is None:
            data = translate_report_data(record.report_data, language)
            record.translations = {**record.translations, language: data}
            db.commit()

    referral_doc = ReferralDocument(**data)
    docx_bytes = generate_referral_docx(referral_doc, language, db)
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="referral_letter_{referral_doc.student_id}.docx"'},
    )


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
