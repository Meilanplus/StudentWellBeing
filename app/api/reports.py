from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import APIRouter, Depends

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.intervention import Intervention, DashboardSummary
from app.schemas.report import DashboardReport, DashboardNarrative, StudentCase, MonthlyKPI, ClassRiskSummary, REPORT_DISCLAIMER
from app.agents.reporting_agent import ReportingAgent
from app.services.report_translator import translate_report_data
from app.services.i18n_lookup import get_translation
from app.services.dashboard_narrative import compute_student_cases, ensure_narrative_generated
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
    """The current period is always live (cheap DB aggregates, recomputed on
    every call). A past period that already has a generated report is a
    locked historical snapshot — its KPIs/class breakdown are read back
    exactly as they were at generation time, not recomputed against today.
    The AI narrative is included ONLY if already cached for this
    period/language; displaying the dashboard never triggers Agent 4 or a
    translation call — see POST /reports/dashboard/narrative for that."""
    agent = ReportingAgent(db)
    resolved_period = period or agent.default_period()
    cached = db.query(DashboardSummary).filter(DashboardSummary.period == resolved_period).first()

    if cached is not None and cached.school_kpis is not None:
        kpis = MonthlyKPI(**cached.school_kpis)
        class_breakdown = [ClassRiskSummary(**c) for c in cached.class_breakdown]
    else:
        kpis, class_breakdown = agent.compute_kpis(resolved_period)

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
        disclaimer=get_translation("report.dashboard_disclaimer", language, db, default=REPORT_DISCLAIMER),
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
    period/language. On first generation for a period, this also freezes
    that period's KPIs/class breakdown/student cases into the same row —
    from then on it's a locked monthly record, immune to later data changes.
    Shares its generation logic with the background pre-generation job (see
    app/services/scheduler.py), so whichever runs first for a given period
    wins and the other just reads the cached row."""
    agent = ReportingAgent(db)
    resolved_period = period or agent.default_period()
    cached = ensure_narrative_generated(resolved_period, db)

    if language == "ms":
        narrative = cached.narrative
    else:
        narrative = cached.translations.get(language)
        if narrative is None:
            narrative = translate_report_data(cached.narrative, language)
            cached.translations = {**cached.translations, language: narrative}
            db.commit()

    return DashboardNarrative(**narrative)


@router.get("/dashboard/periods")
def dashboard_periods(
    requester: User = Depends(require_task(TASK_INVOKE_AGENT4_REPORTING)),
    db: Session = Depends(get_db),
):
    """Periods that already have a generated (locked) report, most recent
    first — powers the Reporting page's "View Previous Reports" list."""
    rows = db.query(DashboardSummary).order_by(DashboardSummary.created_at.desc()).all()
    return [{"period": r.period, "generated_at": r.created_at.isoformat()} for r in rows]


@router.get("/dashboard/cases", response_model=list[StudentCase])
def dashboard_cases(
    period: str | None = None,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT4_REPORTING)),
    db: Session = Depends(get_db),
):
    """The actual students behind a period's KPI counts — full names, never
    passed through Agent 4. Kept off the shared /dashboard response so the
    plain Dashboard page never carries identifiable data; only the Reporting
    page calls this. A past, already-generated period returns its frozen
    case list; anything else (including the current period) is live."""
    agent = ReportingAgent(db)
    resolved_period = period or agent.default_period()
    cached = db.query(DashboardSummary).filter(DashboardSummary.period == resolved_period).first()
    if cached is not None and cached.student_cases is not None:
        return [StudentCase(**c) for c in cached.student_cases]
    return compute_student_cases(db)


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
