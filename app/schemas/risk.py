from datetime import datetime

from pydantic import BaseModel, ConfigDict

RISK_DISCLAIMER = (
    "This risk assessment is generated to support school staff decision-making. "
    "It does NOT constitute a clinical diagnosis or medical advice. All findings "
    "must be reviewed and validated by qualified school counselors."
)
INTERVENTION_DISCLAIMER = (
    "This intervention plan is generated to support school staff decision-making. "
    "It does NOT constitute a clinical diagnosis, psychological assessment, or "
    "treatment plan. All findings must be reviewed and validated by qualified "
    "school counselors before implementation."
)
REFERRAL_DISCLAIMER = (
    "Nota: Dokumen ini disediakan berdasarkan pemerhatian serta rekod sokongan pihak "
    "sekolah bagi tujuan rujukan profesional. Kandungannya tidak bertujuan sebagai "
    "diagnosis klinikal atau menggantikan penilaian oleh pengamal kesihatan yang "
    "berkelayakan."
)


class RiskFactor(BaseModel):
    category: str
    indicator: str
    severity: str
    evidence: str


class TranslateReportRequest(BaseModel):
    report: dict
    target_language: str


class RiskAssessment(BaseModel):
    student_id: str
    student_name: str
    risk_level: str  # "Low Risk" | "Moderate Risk" | "High Risk"
    risk_score: int  # 0-100
    risk_factors: list[RiskFactor]
    summary: str
    recommended_actions: list[str]
    disclaimer: str = RISK_DISCLAIMER


class RiskReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    risk_level: str
    risk_score: int
    report_data: dict
    created_at: datetime


class InterventionAreaPlan(BaseModel):
    area: str
    strategy: str
    responsible: str
    frequency: str
    success_indicator: str


class InterventionRecommendation(BaseModel):
    student_id: str
    student_name: str
    class_name: str
    age: int | None = None
    risk_level: str
    school_name: str
    case_reference: str
    prepared_by: str
    date: str
    language: str = "English"
    reason_for_intervention: list[str]
    intervention_objectives: list[str]
    strategies: list[InterventionAreaPlan]
    recommended_tools: list[str]
    home_strategies: list[str]
    expected_outcomes: list[str]
    monitoring_checklist: list[str]
    counselor_recommendation: str
    action_items_teacher: list[str]
    action_items_counselor: list[str]
    action_items_parent: list[str]
    referral_recommended: bool = False
    referral_reason: str | None = None
    rationale: str
    intervention_id: int | None = None
    disclaimer: str = INTERVENTION_DISCLAIMER


class InterventionReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    risk_level: str
    report_data: dict
    created_at: datetime


class ReferralDocumentRequest(BaseModel):
    student_id: str
    referral_type: str
    referral_to: str
    prepared_by: str
    additional_notes: str | None = None
    language: str = "ms"


class ReferralDocument(BaseModel):
    student_id: str
    student_name: str
    referral_type: str
    referral_to: str
    letter_content: str
    supporting_summary: str
    prepared_by: str
    disclaimer: str = REFERRAL_DISCLAIMER


class ReferralReportSaveRequest(BaseModel):
    document: ReferralDocument
    additional_notes: str | None = None


class ReferralReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    referral_type: str
    referral_to: str
    additional_notes: str | None
    report_data: dict
    created_at: datetime
