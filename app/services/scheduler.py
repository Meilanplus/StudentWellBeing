"""Background pre-generation for Agent 4's monthly dashboard narrative.

Without this, the first person to open Reporting after a new month begins
(or after the previous month's report was generated) pays DeepSeek's live
30-160s+ reasoning time synchronously, staring at the AI-wait timer. This
runs the same generation on a timer instead, so by the time a leader opens
the page the canonical (Bahasa Malaysia) narrative for the current period
is usually already cached — same total DeepSeek cost, just moved off the
user's clock.

ensure_narrative_generated() is a no-op once a period's row exists, so the
daily tick and the startup tick are both cheap (a single query) on every
day but the first of a new month."""
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.agents.reporting_agent import ReportingAgent
from app.database import SessionLocal
from app.services.dashboard_narrative import ensure_narrative_generated

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _generate_current_period_narrative_job() -> None:
    db = SessionLocal()
    try:
        period = ReportingAgent.default_period()
        ensure_narrative_generated(period, db)
    except Exception:
        # A transient DeepSeek/DB failure here should never crash the
        # scheduler thread or the app — the next tick (or an explicit click
        # on "Generate AI Insights") will simply try again.
        logger.exception("Background dashboard narrative pre-generation failed for the current period.")
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    """Idempotent — safe to call once from the app's lifespan startup."""
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler()
    # Runs once shortly after the app starts (covers a server restart that
    # happens to land right after a new month begins, or after the previous
    # month's report was generated) ...
    _scheduler.add_job(
        _generate_current_period_narrative_job,
        trigger="date",
        id="dashboard_narrative_startup",
    )
    # ... and once a day thereafter, so the month rollover is always covered
    # within 24 hours even if the server runs continuously for months.
    _scheduler.add_job(
        _generate_current_period_narrative_job,
        trigger="cron",
        hour=1,
        minute=0,
        id="dashboard_narrative_daily",
    )
    _scheduler.start()
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
