from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.intervention import Intervention
from app.schemas.assessment import InterventionSave, InterventionOut
from app.permissions import require_task
from app.constants import TASK_FILL_STUDENT_DETAIL, TASK_FILL_STUDENT_RELATED_INFO

router = APIRouter(tags=["Interventions"])

ALLOWED_STATUSES = {"active", "completed", "escalated"}


def _get_student_or_404(student_id: str, db: Session) -> Student:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return student


def _get_intervention_or_404(intervention_id: int, db: Session) -> Intervention:
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found.")
    return intervention


@router.post("/students/{student_id}/interventions", response_model=InterventionOut, status_code=201)
def save_intervention(
    student_id: str,
    payload: InterventionSave,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    intervention = Intervention(
        student_id=student.id,
        risk_level=payload.risk_level,
        intervention_type=payload.intervention_type,
        description=payload.description,
        start_date=date.today(),
        assigned_to=payload.assigned_to,
        ai_recommendations=payload.ai_recommendations,
    )
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    return intervention


@router.get("/students/{student_id}/interventions", response_model=list[InterventionOut])
def list_interventions(
    student_id: str,
    status: str | None = None,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_DETAIL, TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    query = db.query(Intervention).filter(Intervention.student_id == student.id)
    if status:
        query = query.filter(Intervention.status == status)
    return query.order_by(Intervention.created_at.desc()).all()


@router.patch("/interventions/{intervention_id}/status", response_model=InterventionOut)
def update_intervention_status(
    intervention_id: int,
    body: dict,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    new_status = body.get("status")
    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of {sorted(ALLOWED_STATUSES)}.")
    intervention = _get_intervention_or_404(intervention_id, db)
    intervention.status = new_status
    if new_status in ("completed", "escalated") and not intervention.end_date:
        intervention.end_date = date.today()
    db.commit()
    db.refresh(intervention)
    return intervention


@router.patch("/interventions/{intervention_id}/outcome", response_model=InterventionOut)
def update_intervention_outcome(
    intervention_id: int,
    body: dict,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    intervention = _get_intervention_or_404(intervention_id, db)
    intervention.outcome_notes = body.get("outcome_notes", intervention.outcome_notes)
    if body.get("end_date"):
        intervention.end_date = date.fromisoformat(body["end_date"])
    db.commit()
    db.refresh(intervention)
    return intervention
