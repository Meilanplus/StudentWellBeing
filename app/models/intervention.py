from datetime import date, datetime

from sqlalchemy import String, Integer, Text, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Intervention(Base):
    __tablename__ = "interventions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)  # low/moderate/high
    intervention_type: Mapped[str] = mapped_column(String(50), nullable=False)  # counseling/academic/parent/ai_comprehensive
    description: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/completed/escalated
    ai_recommendations: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    outcome_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped["Student"] = relationship(back_populates="interventions")


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    referral_date: Mapped[date] = mapped_column(Date, nullable=False)
    referral_type: Mapped[str] = mapped_column(String(50), nullable=False)  # psychiatrist/psychologist/healthcare/kementerian
    referral_to: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    document_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    supporting_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # The school hands this letter to the parent for the parent to take to
    # the specialist — there's no acknowledgement loop back from the
    # receiving professional to track, so this just marks whether the
    # letter has been handed over yet.
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/sent
    prepared_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped["Student"] = relationship(back_populates="referrals")


class RiskReport(Base):
    """A saved Agent 1 risk assessment — only persisted when the counselor
    explicitly clicks Save on the Early Detection page (discarded reports
    are never written here)."""

    __tablename__ = "risk_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    report_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # Cache of on-demand translations, keyed by language code (e.g. {"en": {...}}),
    # so viewing this report in a non-canonical language only pays the LLM
    # translation cost once rather than on every view.
    translations: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    student: Mapped["Student"] = relationship(back_populates="risk_reports")


class InterventionReport(Base):
    """A saved Agent 2 intervention plan — only persisted when the counselor
    explicitly clicks Save on the Intervention page (mirrors RiskReport)."""

    __tablename__ = "intervention_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    report_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    translations: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    student: Mapped["Student"] = relationship(back_populates="intervention_reports")


class ReferralReport(Base):
    """A saved Agent 3 referral letter — only persisted when the counselor
    explicitly clicks Save on the Referral page. Deduplicated by
    (student, referral_type, referral_to), not by date, since a referral
    letter to a given professional doesn't need regenerating just because
    a day has passed (mirrors RiskReport/InterventionReport otherwise)."""

    __tablename__ = "referral_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    referral_type: Mapped[str] = mapped_column(String(50), nullable=False)
    referral_to: Mapped[str] = mapped_column(String(100), nullable=False)
    additional_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    translations: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    student: Mapped["Student"] = relationship(back_populates="referral_reports")


class DashboardSummary(Base):
    """A generated Agent 4 monthly report, keyed by period — a locked
    historical snapshot once created. The narrative (trend_analysis/
    management_summary/recommendations) is canonical in Bahasa Malaysia, with
    on-demand translations cached alongside it (mirrors RiskReport/
    InterventionReport/ReferralReport). school_kpis/class_breakdown/
    student_cases are frozen at the moment the report is first generated for
    that period, so reopening a past month later shows exactly what was true
    then — not today's numbers under an old label. The current (not yet
    generated) period has no row here at all and is computed live; see
    dashboard()/dashboard_cases() in app/api/reports.py. Invalidated (row
    deleted) only for the *current* period whenever a write changes a KPI it
    could describe — see intervene()/generate_referral()/acknowledge_referral
    — never for an already-generated past period, which stays locked."""

    __tablename__ = "dashboard_summaries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    period: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    narrative: Mapped[dict] = mapped_column(JSONB, nullable=False)
    translations: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    school_kpis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    class_breakdown: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    student_cases: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
