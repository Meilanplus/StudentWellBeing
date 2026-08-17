from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.assessment import Assessment, AssessmentResult
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentOut,
    AssessmentResultCreate,
    AssessmentResultOut,
    VanderbiltTeacherAssessmentCreate,
)
from app.services.vanderbilt_scorer import score_teacher_assessment
from app.permissions import require_task
from app.constants import TASK_FILL_STUDENT_DETAIL, TASK_FILL_STUDENT_RELATED_INFO

router = APIRouter(prefix="/assessments", tags=["Assessments"])


def _get_student_or_404(student_id: str, db: Session) -> Student:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return student


@router.post("/", response_model=AssessmentOut, status_code=201)
def create_assessment(
    payload: AssessmentCreate,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_DETAIL, TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    if db.query(Assessment).filter(Assessment.name == payload.name).first():
        raise HTTPException(status_code=409, detail="An assessment instrument with this name already exists.")
    assessment = Assessment(**payload.model_dump())
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/", response_model=list[AssessmentOut])
def list_assessments(
    requester: User = Depends(require_task(TASK_FILL_STUDENT_DETAIL, TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    return db.query(Assessment).order_by(Assessment.name).all()


@router.get("/{instrument_id}", response_model=AssessmentOut)
def get_assessment(
    instrument_id: int,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_DETAIL, TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    assessment = db.query(Assessment).filter(Assessment.id == instrument_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment instrument not found.")
    return assessment


@router.post("/results/{student_id}", response_model=AssessmentResultOut, status_code=201)
def add_assessment_result(
    student_id: str,
    payload: AssessmentResultCreate,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    result = AssessmentResult(student_id=student.id, **payload.model_dump())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("/results/{student_id}", response_model=list[AssessmentResultOut])
def get_assessment_results(
    student_id: str,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_DETAIL, TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)
    return (
        db.query(AssessmentResult)
        .filter(AssessmentResult.student_id == student.id)
        .order_by(AssessmentResult.administered_date.desc())
        .all()
    )


@router.post("/vanderbilt-teacher/{student_id}", response_model=AssessmentResultOut, status_code=201)
def submit_vanderbilt_teacher_assessment(
    student_id: str,
    payload: VanderbiltTeacherAssessmentCreate,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, db)

    instrument_name = "NICHQ Vanderbilt Assessment Scale — Teacher Informant"
    instrument = db.query(Assessment).filter(Assessment.name == instrument_name).first()
    if not instrument:
        instrument = Assessment(
            name=instrument_name,
            instrument_type="behavioral_screening",
            description="NICHQ Vanderbilt ADHD/behavioral screening, teacher-completed.",
        )
        db.add(instrument)
        db.flush()

    scoring = score_teacher_assessment(payload)
    result = AssessmentResult(
        student_id=student.id,
        assessment_id=instrument.id,
        administered_date=payload.administered_date,
        scaled_score=scoring["concern_score_0_100"],
        responses={"input": payload.model_dump(mode="json"), "scoring": scoring},
        observations=payload.comments,
        administered_by=payload.teacher_name,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result
