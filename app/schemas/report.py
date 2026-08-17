from pydantic import BaseModel

REPORT_DISCLAIMER = (
    "This is an AI-assisted summary for school management review. All student "
    "data is anonymized in this summary. Individual student matters must follow "
    "established counseling protocols."
)


class ClassRiskSummary(BaseModel):
    class_name: str
    total_students: int
    low_risk: int
    moderate_risk: int
    high_risk: int


class MonthlyKPI(BaseModel):
    period: str
    total_students: int
    low_risk_count: int
    moderate_risk_count: int
    high_risk_count: int
    active_interventions: int
    referrals_made: int
    referrals_acknowledged: int
    counseling_sessions: int


class DashboardReport(BaseModel):
    generated_at: str
    period: str
    school_kpis: MonthlyKPI
    class_breakdown: list[ClassRiskSummary]
    top_risk_students: list[dict] = []
    trend_analysis: str
    management_summary: str
    recommendations: list[str]
    disclaimer: str = REPORT_DISCLAIMER
