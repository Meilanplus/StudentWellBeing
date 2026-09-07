from sqlalchemy.orm import Session

from app.models.intervention import DashboardSummary


def invalidate_dashboard_cache(db: Session) -> None:
    """Drop all cached dashboard narratives — call this after any write that
    changes a KPI the narrative could describe (a new/updated Intervention or
    Referral). Not scoped by period since these writes are infrequent and a
    stale narrative for any period is worse than an occasional extra
    regeneration."""
    db.query(DashboardSummary).delete()
    db.commit()
