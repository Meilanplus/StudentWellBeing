from datetime import date, datetime

from sqlalchemy import String, Integer, Date, DateTime, Boolean, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    class_name: Mapped[str] = mapped_column(String(20), nullable=False)
    school_year: Mapped[int] = mapped_column(Integer, nullable=False)
    # School scoping — the old project's documented gap: without this, tasks
    # 14/15 (view/edit all data of one/any school) couldn't be enforced on
    # student data, only on staff/User records.
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)
    socioeconomic_status: Mapped[str] = mapped_column(String(20), default="unknown")
    guardian_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    guardian_contact: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    school: Mapped["School"] = relationship()
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    behavior_records: Mapped[list["BehaviorRecord"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    mental_health_records: Mapped[list["MentalHealthRecord"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    nichq_details: Mapped[list["NichqDetail"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    assessment_results: Mapped[list["AssessmentResult"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    interventions: Mapped[list["Intervention"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    referrals: Mapped[list["Referral"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    risk_reports: Mapped[list["RiskReport"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    intervention_reports: Mapped[list["InterventionReport"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    referral_reports: Mapped[list["ReferralReport"]] = relationship(back_populates="student", cascade="all, delete-orphan")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    att_per: Mapped[str] = mapped_column(String(20), nullable=False)  # attendance percentage, e.g. "95%"
    reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    recorded_by: Mapped[str] = mapped_column(String(100), nullable=False)

    student: Mapped["Student"] = relationship(back_populates="attendance_records")


class BehaviorRecord(Base):
    __tablename__ = "behavior_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    incident_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    incident_type: Mapped[str] = mapped_column(String(50), nullable=False)  # discipline/emotional/academic
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # minor/moderate/serious
    description: Mapped[str] = mapped_column(Text, nullable=False)
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    reported_by: Mapped[str] = mapped_column(String(100), nullable=False)

    student: Mapped["Student"] = relationship(back_populates="behavior_records")


class MentalHealthRecord(Base):
    __tablename__ = "mental_health_records"
    __table_args__ = (
        CheckConstraint("gad2_score >= 0 AND gad2_score <= 9", name="ck_mental_health_records_gad2_score_digit"),
        CheckConstraint("semester >= 0 AND semester <= 9", name="ck_mental_health_records_semester_digit"),
        CheckConstraint("year >= 1000 AND year <= 9999", name="ck_mental_health_records_year_4digit"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    whooley: Mapped[str] = mapped_column(String(10), nullable=False)  # Positive/Negative
    gad2_score: Mapped[int] = mapped_column(Integer, nullable=False)  # single digit, 0-9
    gad2_status: Mapped[str] = mapped_column(String(10), nullable=False)  # Positive/Negative
    semester: Mapped[int] = mapped_column(Integer, nullable=False)  # single digit, 0-9
    year: Mapped[int] = mapped_column(Integer, nullable=False)  # 4-digit year

    student: Mapped["Student"] = relationship(back_populates="mental_health_records")


class NichqDetail(Base):
    __tablename__ = "nichq_detail"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    inattentive: Mapped[int] = mapped_column(Integer, nullable=False)
    hyperactive: Mapped[int] = mapped_column(Integer, nullable=False)
    performance: Mapped[int] = mapped_column(Integer, nullable=False)

    student: Mapped["Student"] = relationship(back_populates="nichq_details")
