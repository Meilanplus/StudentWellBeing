"""Shared Agent 4 (Reporting) narrative logic — used by both the explicit
POST /reports/dashboard/narrative endpoint and the background pre-generation
job (app/services/scheduler.py). Centralizing this means a leader who opens
the Reporting page after the background job has already run for the current
period just reads the cached row instantly, exactly as if they had clicked
"Generate AI Insights" themselves."""
from datetime import date, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.agents.reporting_agent import ReportingAgent
from app.models.intervention import DashboardSummary, Intervention, Referral
from app.models.student import Student
from app.schemas.report import StudentCase


def compute_student_cases(db: Session) -> list[StudentCase]:
    """The actual students behind the current KPI counts — full names,
    queried directly from the DB (never passed through Agent 4). Always a
    live, current-moment computation; callers freeze the result into a
    DashboardSummary row at generation time if it needs to become a
    historical snapshot."""
    since_30 = date.today() - timedelta(days=30)
    cases: dict[int, StudentCase] = {}

    active_interventions = (
        db.query(Intervention, Student)
        .join(Student, Student.id == Intervention.student_id)
        .filter(Intervention.status == "active")
        .all()
    )
    for interv, student in active_interventions:
        cases[student.id] = StudentCase(
            student_id=student.student_id,
            name=student.full_name,
            class_name=student.class_name,
            risk_level=interv.risk_level,
            intervention_status=interv.status,
        )

    recent_referrals = (
        db.query(Referral, Student)
        .join(Student, Student.id == Referral.student_id)
        .filter(Referral.created_at >= since_30)
        .all()
    )
    for referral, student in recent_referrals:
        existing = cases.get(student.id)
        if existing:
            existing.referral_status = referral.status
        else:
            cases[student.id] = StudentCase(
                student_id=student.student_id,
                name=student.full_name,
                class_name=student.class_name,
                referral_status=referral.status,
            )

    return sorted(cases.values(), key=lambda c: c.name)


def ensure_narrative_generated(period: str, db: Session) -> DashboardSummary:
    """Generates and freezes the canonical (Bahasa Malaysia) narrative for a
    period if it doesn't already exist; otherwise returns the existing row
    untouched and does NOT call Agent 4 again. Safe to call speculatively —
    the background pre-generation job calls this on a timer, and the POST
    endpoint calls it on an explicit user click; whichever gets there first
    generates it, the other just reads the cached result."""
    cached = db.query(DashboardSummary).filter(DashboardSummary.period == period).first()
    if cached is not None:
        return cached

    agent = ReportingAgent(db)
    kpis, class_breakdown = agent.compute_kpis(period)
    narrative = agent.generate_narrative(period, kpis, class_breakdown, language="Bahasa Malaysia")
    cached = DashboardSummary(
        period=period,
        narrative=narrative,
        school_kpis=kpis.model_dump(),
        class_breakdown=[c.model_dump() for c in class_breakdown],
        student_cases=[c.model_dump() for c in compute_student_cases(db)],
    )
    db.add(cached)
    try:
        db.commit()
        db.refresh(cached)
    except IntegrityError:
        # Another concurrent caller (e.g. the scheduled job and a leader's
        # click landing at the same time) won the race and committed first —
        # use its row instead of erroring.
        db.rollback()
        cached = db.query(DashboardSummary).filter(DashboardSummary.period == period).first()
    return cached
