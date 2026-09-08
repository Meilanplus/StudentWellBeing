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
    # None when the AI narrative hasn't been generated yet for this
    # period/language — KPIs are always live, but Agent 4 only runs when
    # explicitly requested (see POST /reports/dashboard/narrative), never
    # just because the dashboard is being displayed.
    trend_analysis: str | None = None
    management_summary: str | None = None
    recommendations: list[str] | None = None
    disclaimer: str = REPORT_DISCLAIMER


class DashboardNarrative(BaseModel):
    trend_analysis: str
    management_summary: str
    recommendations: list[str]
