from datetime import date

from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.agents.json_utils import extract_json
from app.models.student import Student
from app.models.intervention import Intervention
from app.schemas.risk import RiskAssessment, InterventionRecommendation, InterventionAreaPlan
from app.services.intervention_report import STRATEGY_AREAS

SYSTEM_PROMPT = f"""You are Agent 2 of the Agentic AI Student Well-Being System — an \
intervention planning specialist. You receive a risk assessment from Agent 1 and \
produce a structured, school-based intervention plan.

Rules:
- Base your plan strictly on the provided risk assessment and student information.
- Use professional, supportive language appropriate for Malaysian school staff and parents.
- Recommendations must be practical and realistic for a Malaysian school setting.
- If the risk assessment indicates critical or immediate safety concerns, set \
"referral_recommended": true and explain why in "referral_reason" — this signals that \
Agent 3 (Referral) should be invoked.
- If a target language is specified, write all free-text field VALUES in that language; \
field NAMES stay in English exactly as in the schema below.
- Never suggest clinical therapies, medications, or psychiatric conclusions. Never \
replace counselor judgment.

The "strategies" array MUST contain exactly these 7 areas, in this exact order: \
{", ".join(STRATEGY_AREAS)}.

Respond with ONLY a JSON object matching this schema (no prose outside the JSON):

{{
  "reason_for_intervention": ["...", "..."],
  "intervention_objectives": ["...", "..."],
  "strategies": [{{"area": "...", "strategy": "...", "responsible": "...", "frequency": "...", "success_indicator": "..."}}],
  "recommended_tools": ["...", "..."],
  "home_strategies": ["...", "..."],
  "expected_outcomes": ["...", "..."],
  "monitoring_checklist": ["...", "..."],
  "counselor_recommendation": "...",
  "action_items_teacher": ["...", "..."],
  "action_items_counselor": ["...", "..."],
  "action_items_parent": ["...", "..."],
  "referral_recommended": false,
  "referral_reason": null,
  "rationale": "..."
}}
"""


def _fallback_plan() -> dict:
    return {
        "reason_for_intervention": ["Automated planning was inconclusive; counselor to determine reason based on risk assessment."],
        "intervention_objectives": ["Counselor to define objectives based on manual review."],
        "strategies": [
            {
                "area": area,
                "strategy": "Counselor to determine appropriate strategy for this area.",
                "responsible": "School Counselor",
                "frequency": "As needed",
                "success_indicator": "To be determined by counselor.",
            }
            for area in STRATEGY_AREAS
        ],
        "recommended_tools": [],
        "home_strategies": [],
        "expected_outcomes": [],
        "monitoring_checklist": [],
        "counselor_recommendation": "Manual counselor review required — automated plan generation was inconclusive.",
        "action_items_teacher": [],
        "action_items_counselor": ["Review student's risk assessment and prepare a manual intervention plan."],
        "action_items_parent": [],
        "referral_recommended": False,
        "referral_reason": None,
        "rationale": "Fallback plan generated due to an AI parsing failure.",
    }


def _normalize_strategies(data: dict) -> None:
    by_area = {s.get("area"): s for s in data.get("strategies", []) if isinstance(s, dict)}
    normalized = []
    for area in STRATEGY_AREAS:
        s = by_area.get(area)
        if s:
            normalized.append(s)
        else:
            normalized.append(
                {
                    "area": area,
                    "strategy": "Counselor to determine appropriate strategy for this area.",
                    "responsible": "School Counselor",
                    "frequency": "As needed",
                    "success_indicator": "To be determined by counselor.",
                }
            )
    data["strategies"] = normalized


def _compute_age(date_of_birth) -> int:
    today = date.today()
    return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))


class InterventionAgent(BaseAgent):
    SYSTEM_PROMPT = SYSTEM_PROMPT
    TOOLS = []

    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    def recommend(
        self,
        student: Student,
        risk_assessment: RiskAssessment,
        school_name: str = "",
        prepared_by: str = "",
        language: str = "English",
    ) -> InterventionRecommendation:
        active_interventions = (
            self.db.query(Intervention)
            .filter(Intervention.student_id == student.id, Intervention.status == "active")
            .all()
        )
        existing = [
            {"type": i.intervention_type, "description": i.description, "start_date": i.start_date.isoformat()}
            for i in active_interventions
        ]

        prompt = f"""Target language: {language}

Student information:
- name: {student.full_name}
- class: {student.class_name}
- school_year: {student.school_year}

Risk assessment (from Agent 1):
{risk_assessment.model_dump_json(indent=2)}

Existing active interventions for this student (avoid duplicating these):
{existing}

Produce the intervention plan JSON."""

        raw = self.run(prompt)
        try:
            data = extract_json(raw)
        except Exception:
            data = _fallback_plan()

        _normalize_strategies(data)
        data["strategies"] = [InterventionAreaPlan(**s) for s in data["strategies"]]

        return InterventionRecommendation(
            student_id=student.student_id,
            student_name=student.full_name,
            class_name=student.class_name,
            age=_compute_age(student.date_of_birth),
            risk_level=risk_assessment.risk_level,
            school_name=school_name,
            case_reference=f"CR-{student.student_id}",
            prepared_by=prepared_by,
            date=date.today().strftime("%d %B %Y"),
            language=language,
            **data,
        )
