from datetime import date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.agents.base_agent import BaseAgent
from app.agents.json_utils import extract_json
from app.models.student import Student
from app.models.intervention import Intervention, Referral
from app.schemas.report import DashboardReport, MonthlyKPI, ClassRiskSummary

SYSTEM_PROMPT = """You are Agent 4 of the Agentic AI Student Well-Being System — a \
school well-being reporting specialist producing management dashboards for \
principals, counselors, and Penolong Kanan HEM (assistant headmasters).

Rules:
- Present data factually — do not exaggerate or minimize.
- Highlight trends that need leadership attention.
- Use professional language appropriate for school leadership review.
- Protect privacy: never name individual students in the management summary — this is \
an aggregate/anonymized view.

You will be given aggregated KPI and class-breakdown data (already computed — you do \
not need tools). Respond with ONLY a JSON object matching this schema (no prose \
outside the JSON):

{
  "trend_analysis": "...",
  "management_summary": "...",
  "recommendations": ["...", "..."]
}
"""


class ReportingAgent(BaseAgent):
    SYSTEM_PROMPT = SYSTEM_PROMPT
    TOOLS = []

    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    def _compute_kpis(self, period: str) -> tuple[MonthlyKPI, list[ClassRiskSummary]]:
        since_30 = date.today() - timedelta(days=30)

        total_students = self.db.query(Student).filter(Student.is_active.is_(True)).count()
        active_interventions = self.db.query(Intervention).filter(Intervention.status == "active").count()
        referrals_made = self.db.query(Referral).filter(Referral.created_at >= since_30).count()
        referrals_acknowledged = (
            self.db.query(Referral)
            .filter(Referral.status == "acknowledged", Referral.created_at >= since_30)
            .count()
        )
        counseling_sessions = (
            self.db.query(Intervention)
            .filter(Intervention.intervention_type == "counseling", Intervention.created_at >= since_30)
            .count()
        )

        active_by_risk_and_class = (
            self.db.query(Student.class_name, Intervention.risk_level, func.count(func.distinct(Student.id)))
            .join(Intervention, Intervention.student_id == Student.id)
            .filter(Intervention.status == "active")
            .group_by(Student.class_name, Intervention.risk_level)
            .all()
        )
        students_per_class = dict(
            self.db.query(Student.class_name, func.count(Student.id))
            .filter(Student.is_active.is_(True))
            .group_by(Student.class_name)
            .all()
        )

        breakdown: dict[str, dict[str, int]] = {}
        for class_name, risk_level, count in active_by_risk_and_class:
            entry = breakdown.setdefault(class_name, {"low": 0, "moderate": 0, "high": 0})
            key = risk_level.lower() if risk_level and risk_level.lower() in entry else None
            if key:
                entry[key] += count

        class_breakdown = [
            ClassRiskSummary(
                class_name=class_name,
                total_students=students_per_class.get(class_name, 0),
                low_risk=counts["low"],
                moderate_risk=counts["moderate"],
                high_risk=counts["high"],
            )
            for class_name, counts in sorted(breakdown.items())
        ]

        low_total = sum(c.low_risk for c in class_breakdown)
        moderate_total = sum(c.moderate_risk for c in class_breakdown)
        high_total = sum(c.high_risk for c in class_breakdown)

        kpis = MonthlyKPI(
            period=period,
            total_students=total_students,
            low_risk_count=low_total,
            moderate_risk_count=moderate_total,
            high_risk_count=high_total,
            active_interventions=active_interventions,
            referrals_made=referrals_made,
            referrals_acknowledged=referrals_acknowledged,
            counseling_sessions=counseling_sessions,
        )
        return kpis, class_breakdown

    def generate_dashboard(self, period: str | None = None) -> DashboardReport:
        period = period or date.today().strftime("%B %Y")
        kpis, class_breakdown = self._compute_kpis(period)

        prompt = f"""Monthly KPI data:
{kpis.model_dump_json(indent=2)}

Class risk breakdown:
{[c.model_dump() for c in class_breakdown]}

Write the narrative sections (trend_analysis, management_summary, recommendations) as JSON."""

        raw = self.run(prompt)
        try:
            data = extract_json(raw)
        except Exception:
            data = {
                "trend_analysis": "Trend data unavailable due to an automated generation failure. Please review the KPI figures directly.",
                "management_summary": "Automated summary unavailable. Raw KPI data is provided above for manual review.",
                "recommendations": [],
            }

        return DashboardReport(
            generated_at=date.today().isoformat(),
            period=period,
            school_kpis=kpis,
            class_breakdown=class_breakdown,
            top_risk_students=[],
            **data,
        )
