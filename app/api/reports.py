from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.intervention import Intervention, DashboardSummary
from app.schemas.report import DashboardReport, DashboardNarrative
from app.agents.reporting_agent import ReportingAgent
from app.services.report_translator import translate_report_data
from app.permissions import require_task
from app.constants import TASK_INVOKE_AGENT4_REPORTING

router = APIRouter(prefix="/reports", tags=["Dashboard & Reports"])


@router.get("/dashboard", response_model=DashboardReport)
def dashboard(
    period: str | None = None,
    language: str = "ms",
    requester: User = Depends(require_task(TASK_INVOKE_AGENT4_REPORTING)),
    db: Session = Depends(get_db),
):
    """KPIs are cheap DB aggregates — always recomputed live. The AI narrative
    is included ONLY if already cached for this period/language; displaying
    the dashboard never triggers Agent 4 or a translation call. Generating
    it (first time for a period, or a new language) is a separate, explicit
    action — see POST /reports/dashboard/narrative."""
    agent = ReportingAgent(db)
    resolved_period = period or agent.default_period()
    kpis, class_breakdown = agent.compute_kpis(resolved_period)

    cached = db.query(DashboardSummary).filter(DashboardSummary.period == resolved_period).first()
    narrative: dict = {}
    if cached is not None:
        if language == "ms":
            narrative = cached.narrative
        else:
            narrative = cached.translations.get(language) or {}

    return DashboardReport(
        generated_at=date.today().isoformat(),
        period=resolved_period,
        school_kpis=kpis,
        class_breakdown=class_breakdown,
        top_risk_students=[],
        **narrative,
    )


@router.post("/dashboard/narrative", response_model=DashboardNarrative)
def generate_dashboard_narrative(
    period: str | None = None,
    language: str = "ms",
    requester: User = Depends(require_task(TASK_INVOKE_AGENT4_REPORTING)),
    db: Session = Depends(get_db),
):
    """Explicitly generates (or serves the cached) Agent 4 narrative for a
    period/language — the only place that ever invokes Agent 4 or a
    translation call, so the dashboard's default display never blocks on it."""
    agent = ReportingAgent(db)
    resolved_period = period or agent.default_period()
    kpis, class_breakdown = agent.compute_kpis(resolved_period)

    cached = db.query(DashboardSummary).filter(DashboardSummary.period == resolved_period).first()
    if cached is None:
        narrative = agent.generate_narrative(resolved_period, kpis, class_breakdown, language="Bahasa Malaysia")
        cached = DashboardSummary(period=resolved_period, narrative=narrative)
        db.add(cached)
        try:
            db.commit()
            db.refresh(cached)
        except IntegrityError:
            # Another concurrent request for the same period won the race and
            # committed first — use its row instead of erroring.
            db.rollback()
            cached = db.query(DashboardSummary).filter(DashboardSummary.period == resolved_period).first()

    if language == "ms":
        narrative = cached.narrative
    else:
        narrative = cached.translations.get(language)
        if narrative is None:
            narrative = translate_report_data(cached.narrative, language)
            cached.translations = {**cached.translations, language: narrative}
            db.commit()

    return DashboardNarrative(**narrative)


@router.get("/class-summary")
def class_summary(
    requester: User = Depends(require_task(TASK_INVOKE_AGENT4_REPORTING)),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Student.class_name, Intervention.risk_level, func.count(func.distinct(Student.id)))
        .join(Intervention, Intervention.student_id == Student.id)
        .filter(Intervention.status == "active")
        .group_by(Student.class_name, Intervention.risk_level)
        .all()
    )
    students_per_class = dict(
        db.query(Student.class_name, func.count(Student.id))
        .filter(Student.is_active.is_(True))
        .group_by(Student.class_name)
        .all()
    )

    breakdown: dict[str, dict[str, int]] = {}
    for class_name, risk_level, count in rows:
        entry = breakdown.setdefault(class_name, {"low": 0, "moderate": 0, "high": 0})
        # risk_level is stored as "Low Risk" / "Moderate Risk" / "High Risk" —
        # take the first word so it matches entry's bare "low"/"moderate"/"high" keys.
        key = risk_level.lower().split()[0] if risk_level else None
        if key not in entry:
            key = None
        if key:
            entry[key] += count

    return [
        {
            "class_name": class_name,
            "total_students": students_per_class.get(class_name, 0),
            "low_risk": counts["low"],
            "moderate_risk": counts["moderate"],
            "high_risk": counts["high"],
        }
        for class_name, counts in sorted(breakdown.items())
    ]
