from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.student import Student, AttendanceRecord, BehaviorRecord, MentalHealthRecord
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentOut,
    AttendanceRecordCreate,
    AttendanceRecordOut,
    AttendanceRecordUpdate,
    BehaviorRecordCreate,
    BehaviorRecordOut,
    BehaviorRecordUpdate,
    MentalHealthRecordCreate,
    MentalHealthRecordOut,
    MentalHealthRecordUpdate,
)
from app.permissions import require_task, get_role_task_ids
from app.constants import (
    TASK_FILL_STUDENT_DETAIL,
    TASK_FILL_STUDENT_RELATED_INFO,
    TASK_VIEW_EDIT_ALL_DATA_ANY_SCHOOL,
)

router = APIRouter(prefix="/students", tags=["Students"])


def _can_see_any_school(user: User, db: Session) -> bool:
    return TASK_VIEW_EDIT_ALL_DATA_ANY_SCHOOL in get_role_task_ids(user.role_id, db)


def _scope_query(query, user: User, db: Session):
    if _can_see_any_school(user, db):
        return query
    return query.filter(Student.school_id == user.school_id)


def _get_student_or_404(student_id: str, user: User, db: Session) -> Student:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    if not _can_see_any_school(user, db) and student.school_id != user.school_id:
        raise HTTPException(status_code=403, detail="Student belongs to a different school.")
    return student


@router.post("/", response_model=StudentOut, status_code=201)
def create_student(
    payload: StudentCreate,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_DETAIL)),
    db: Session = Depends(get_db),
):
    if not _can_see_any_school(requester, db) and payload.school_id != requester.school_id:
        raise HTTPException(status_code=403, detail="Cannot register a student for a different school.")
    if db.query(Student).filter(Student.student_id == payload.student_id).first():
        raise HTTPException(status_code=409, detail="A student with this student_id already exists.")
    student = Student(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/", response_model=list[StudentOut])
def list_students(
    class_name: str | None = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_DETAIL, TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    query = _scope_query(db.query(Student), requester, db)
    if class_name:
        query = query.filter(Student.class_name == class_name)
    if active_only:
        query = query.filter(Student.is_active.is_(True))
    return query.offset(skip).limit(limit).all()


@router.get("/{student_id}", response_model=StudentOut)
def get_student(
    student_id: str,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_DETAIL, TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    return _get_student_or_404(student_id, requester, db)


@router.patch("/{student_id}", response_model=StudentOut)
def update_student(
    student_id: str,
    payload: StudentUpdate,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_DETAIL)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, requester, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


@router.post("/{student_id}/attendance", response_model=AttendanceRecordOut, status_code=201)
def add_attendance(
    student_id: str,
    payload: AttendanceRecordCreate,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, requester, db)
    record = AttendanceRecord(student_id=student.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{student_id}/attendance", response_model=list[AttendanceRecordOut])
def get_attendance(
    student_id: str,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_DETAIL, TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, requester, db)
    return db.query(AttendanceRecord).filter(AttendanceRecord.student_id == student.id).order_by(AttendanceRecord.record_date.desc()).all()


@router.patch("/{student_id}/attendance/{record_id}", response_model=AttendanceRecordOut)
def update_attendance(
    student_id: str,
    record_id: int,
    payload: AttendanceRecordUpdate,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, requester, db)
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id, AttendanceRecord.student_id == student.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.post("/{student_id}/behavior", response_model=BehaviorRecordOut, status_code=201)
def add_behavior(
    student_id: str,
    payload: BehaviorRecordCreate,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, requester, db)
    record = BehaviorRecord(student_id=student.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{student_id}/behavior", response_model=list[BehaviorRecordOut])
def get_behavior(
    student_id: str,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_DETAIL, TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, requester, db)
    return db.query(BehaviorRecord).filter(BehaviorRecord.student_id == student.id).order_by(BehaviorRecord.incident_date.desc()).all()


@router.patch("/{student_id}/behavior/{record_id}", response_model=BehaviorRecordOut)
def update_behavior(
    student_id: str,
    record_id: int,
    payload: BehaviorRecordUpdate,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, requester, db)
    record = db.query(BehaviorRecord).filter(BehaviorRecord.id == record_id, BehaviorRecord.student_id == student.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Behavior record not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.post("/{student_id}/mental-health", response_model=MentalHealthRecordOut, status_code=201)
def add_mental_health_record(
    student_id: str,
    payload: MentalHealthRecordCreate,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, requester, db)
    record = MentalHealthRecord(student_id=student.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{student_id}/mental-health", response_model=list[MentalHealthRecordOut])
def get_mental_health_records(
    student_id: str,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_DETAIL, TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, requester, db)
    return (
        db.query(MentalHealthRecord)
        .filter(MentalHealthRecord.student_id == student.id)
        .order_by(MentalHealthRecord.year.desc(), MentalHealthRecord.semester.desc())
        .all()
    )


@router.patch("/{student_id}/mental-health/{record_id}", response_model=MentalHealthRecordOut)
def update_mental_health_record(
    student_id: str,
    record_id: int,
    payload: MentalHealthRecordUpdate,
    requester: User = Depends(require_task(TASK_FILL_STUDENT_RELATED_INFO)),
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(student_id, requester, db)
    record = (
        db.query(MentalHealthRecord)
        .filter(MentalHealthRecord.id == record_id, MentalHealthRecord.student_id == student.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Mental health record not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record
