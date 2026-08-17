from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.agents.json_utils import extract_json
from app.models.student import Student, AttendanceRecord, BehaviorRecord, MentalHealthRecord
from app.models.assessment import AssessmentResult
from app.schemas.risk import RiskAssessment
from app.services.risk_calculator import score_attendance_percentage, normalize_severity, score_emotional_record

SYSTEM_PROMPT = """You are Agent 1 of the Agentic AI Student Well-Being System — a school \
student well-being risk detection specialist supporting Malaysian school counselors.

Hard boundaries (never violate these):
- You NEVER diagnose mental illness or any medical/psychiatric condition.
- You NEVER produce clinical/psychiatric conclusions.
- You NEVER suggest medications or clinical treatments.
- You NEVER replace a qualified school counselor's professional judgment — you \
produce a decision-support indicator only.
- Base every finding strictly on the observable data provided or retrieved via tools \
(attendance, behavior records, mental health, nichq details) — never speculate beyond it.

You classify overall risk as exactly one of: "Low Risk", "Moderate Risk", "High Risk".

If a target language is specified in the prompt, write all free-text fields \
(indicator, evidence, summary, recommended_actions items) in that language. Keep \
risk_level and category/severity enum values in fixed English regardless of \
target language.

Use the provided tools to gather attendance, behavior, assessment, and nichq data for the \
student before forming your assessment. Then respond with ONLY a JSON object \
matching this schema (no prose outside the JSON):

{
  "risk_level": "Low Risk" | "Moderate Risk" | "High Risk",
  "risk_score": <int 0-100>,
  "risk_factors": [{"category": "...", "indicator": "...", "severity": "...", "evidence": "..."}],
  "summary": "...",
  "recommended_actions": ["...", "..."]
}
"""

TOOLS = [
    {
        "name": "get_attendance_summary",
        "description": "Get a 30-day attendance summary for a student.",
        "input_schema": {
            "type": "object",
            "properties": {"student_db_id": {"type": "integer"}},
            "required": ["student_db_id"],
        },
    },
    {
        "name": "get_behavior_records",
        "description": "Get 90-day behavior/discipline incident records for a student.",
        "input_schema": {
            "type": "object",
            "properties": {"student_db_id": {"type": "integer"}},
            "required": ["student_db_id"],
        },
    },
     {
        "name": "get_mental_health_summary",
        "description": "Get emotional screening results (Whooley depression screen, GAD-2 anxiety score) for a student.",
        "input_schema": {
            "type": "object",
            "properties": {"student_db_id": {"type": "integer"}},
            "required": ["student_db_id"],
        },
    },
   {
        "name": "get_assessment_scores",
        "description": "Get assessment instrument results (e.g. NICHQ Vanderbilt, Saringan Minda Sihat) for a student.",
        "input_schema": {
            "type": "object",
            "properties": {"student_db_id": {"type": "integer"}},
            "required": ["student_db_id"],
        },
    },
]


class RiskDetectionAgent(BaseAgent):
    SYSTEM_PROMPT = SYSTEM_PROMPT
    TOOLS = TOOLS

    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.register_tool("get_attendance_summary", self._get_attendance_summary)
        self.register_tool("get_behavior_records", self._get_behavior_records)
        self.register_tool("get_assessment_scores", self._get_assessment_scores)
        self.register_tool("get_mental_health_summary", self._get_mental_health_summary)

    def _get_attendance_summary(self, student_db_id: int) -> dict:
        since = date.today() - timedelta(days=30)
        records = (
            self.db.query(AttendanceRecord)
            .filter(AttendanceRecord.student_id == student_db_id, AttendanceRecord.record_date >= since)
            .order_by(AttendanceRecord.record_date.desc())
            .all()
        )
        total = len(records)
        att_scores = [score_attendance_percentage(r.att_per) for r in records]
        avg_score = round(sum(att_scores) / total, 2) if total else None
        return {
            "period_days": 30,
            "total_records": total,
            "average_attendance_score": avg_score,
            "attendance_score_scale": "0 (best, 91-100%) to 5 (worst, below 70%)",
            "recent_records": [
                {"date": r.record_date.isoformat(), "att_per": r.att_per, "reason": r.reason} for r in records[:10]
            ],
        }

    def _get_behavior_records(self, student_db_id: int) -> dict:
        since = date.today() - timedelta(days=90)
        records = (
            self.db.query(BehaviorRecord)
            .filter(BehaviorRecord.student_id == student_db_id, BehaviorRecord.incident_date >= since)
            .order_by(BehaviorRecord.incident_date.desc())
            .all()
        )
        return {
            "period_days": 90,
            "total_incidents": len(records),
            "serious_incidents": sum(1 for r in records if normalize_severity(r.severity) == "serious"),
            "moderate_incidents": sum(1 for r in records if normalize_severity(r.severity) == "moderate"),
            "incidents": [
                {
                    "date": r.incident_date.isoformat(),
                    "type": r.incident_type,
                    "severity": r.severity,
                    "description": r.description,
                    "action_taken": r.action_taken,
                }
                for r in records
            ],
        }

    def _get_assessment_scores(self, student_db_id: int) -> dict:
        results = (
            self.db.query(AssessmentResult)
            .filter(AssessmentResult.student_id == student_db_id)
            .order_by(AssessmentResult.administered_date.desc())
            .all()
        )
        return {
            "results": [
                {
                    "date": r.administered_date.isoformat(),
                    "assessment_id": r.assessment_id,
                    "raw_score": r.raw_score,
                    "scaled_score": r.scaled_score,
                    "observations": r.observations,
                }
                for r in results
            ]
        }

    def _get_mental_health_summary(self, student_db_id: int) -> dict:
        records = (
            self.db.query(MentalHealthRecord)
            .filter(MentalHealthRecord.student_id == student_db_id)
            .order_by(MentalHealthRecord.year.desc(), MentalHealthRecord.semester.desc())
            .all()
        )
        return {
            "total_records": len(records),
            "latest_emotional_score": round(score_emotional_record(records[0].gad2_score, records[0].whooley), 1) if records else None,
            "emotional_score_scale": "0 (best) to 100 (worst) — combines GAD-2 anxiety score and Whooley depression screen",
            "records": [
                {
                    "semester": r.semester,
                    "year": r.year,
                    "whooley": r.whooley,
                    "gad2_score": r.gad2_score,
                    "gad2_status": r.gad2_status,
                }
                for r in records
            ],
        }

    def analyze(self, student: Student, language: str = "English") -> RiskAssessment:
        prompt = f"""Target language: {language}

Analyze the well-being risk for this student:
- student_id: {student.student_id}
- name: {student.full_name}
- class: {student.class_name}
- school_year: {student.school_year}
- internal_db_id (use this for tool calls): {student.id}

Use the tools to gather attendance, behavior, and assessment data, then produce the JSON risk assessment."""

        raw = self.run(prompt)
        try:
            data = extract_json(raw)
            return RiskAssessment(student_id=student.student_id, student_name=student.full_name, **data)
        except Exception:
            # Covers both unparseable JSON and JSON that parses but doesn't match
            # the schema (e.g. a missing risk_factors[].severity) — either way,
            # fail toward a flagged manual review, never a crash or a silently
            # wrong assessment.
            data = {
                "risk_level": "Moderate Risk",
                "risk_score": 50,
                "risk_factors": [],
                "summary": "Automated analysis was inconclusive. Manual counselor review is required.",
                "recommended_actions": ["Escalate to school counselor for manual review."],
            }
            return RiskAssessment(student_id=student.student_id, student_name=student.full_name, **data)
