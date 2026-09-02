from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import APIRouter, Depends

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.intervention import Intervention
from app.schemas.report import DashboardReport
from app.agents.reporting_agent import ReportingAgent
from app.permissions import require_task
from app.constants import TASK_INVOKE_AGENT4_REPORTING

router = APIRouter(prefix="/reports", tags=["Dashboard & Reports"])


@router.get("/dashboard", response_model=DashboardReport)
def dashboard(
    period: str | None = None,
    requester: User = Depends(require_task(TASK_INVOKE_AGENT4_REPORTING)),
    db: Session = Depends(get_db),
):
    agent = ReportingAgent(db)
    return agent.generate_dashboard(period)


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
