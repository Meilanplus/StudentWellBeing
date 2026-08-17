from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class StudentBase(BaseModel):
    student_id: str
    full_name: str
    date_of_birth: date
    gender: str
    class_name: str
    school_year: int
    school_id: int
    socioeconomic_status: str = "unknown"
    guardian_name: str | None = None
    guardian_contact: str | None = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    full_name: str | None = None
    class_name: str | None = None
    school_year: int | None = None
    socioeconomic_status: str | None = None
    guardian_name: str | None = None
    guardian_contact: str | None = None
    is_active: bool | None = None


class StudentOut(StudentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    created_at: datetime


class AttendanceRecordCreate(BaseModel):
    record_date: date
    att_per: str
    reason: str | None = None
    recorded_by: str


class AttendanceRecordOut(AttendanceRecordCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int


class AttendanceRecordUpdate(BaseModel):
    record_date: date | None = None
    att_per: str | None = None
    reason: str | None = None
    recorded_by: str | None = None


class BehaviorRecordCreate(BaseModel):
    incident_date: date
    incident_type: str
    severity: str
    description: str
    action_taken: str | None = None
    reported_by: str


class BehaviorRecordOut(BehaviorRecordCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int


class BehaviorRecordUpdate(BaseModel):
    incident_date: date | None = None
    incident_type: str | None = None
    severity: str | None = None
    description: str | None = None
    action_taken: str | None = None
    reported_by: str | None = None


class MentalHealthRecordCreate(BaseModel):
    whooley: str
    gad2_score: int
    gad2_status: str
    semester: int
    year: int


class MentalHealthRecordOut(MentalHealthRecordCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int


class MentalHealthRecordUpdate(BaseModel):
    whooley: str | None = None
    gad2_score: int | None = None
    gad2_status: str | None = None
    semester: int | None = None
    year: int | None = None
