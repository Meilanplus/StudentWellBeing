from datetime import date, datetime

from sqlalchemy import String, Text, Date, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Assessment(Base):
    """Instrument definition (e.g. NICHQ Vanderbilt, Saringan Minda Sihat, SDQ)."""

    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    instrument_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scoring_guide: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    results: Mapped[list["AssessmentResult"]] = relationship(back_populates="assessment")


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), nullable=False)
    administered_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    raw_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    scaled_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    responses: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    administered_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped["Student"] = relationship(back_populates="assessment_results")
    assessment: Mapped["Assessment"] = relationship(back_populates="results")
