from datetime import date

from sqlalchemy.orm import Session

from app.models.intervention import DashboardSummary


def invalidate_dashboard_cache(db: Session) -> None:
    """Drop the *current* period's cached report — call this after any write
    that changes a KPI it could describe (a new/updated Intervention or
    Referral). Scoped to the current period only: once a past month's report
    has been generated it's a locked historical snapshot (frozen KPIs, class
    breakdown, and student cases alongside the narrative) and must never be
    silently altered by later, unrelated writes."""
    current_period = date.today().strftime("%B %Y")
    db.query(DashboardSummary).filter(DashboardSummary.period == current_period).delete()
    db.commit()
