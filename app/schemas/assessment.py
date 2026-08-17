from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class AssessmentCreate(BaseModel):
    name: str
    instrument_type: str
    description: str | None = None
    scoring_guide: dict | None = None


class AssessmentOut(AssessmentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class AssessmentResultCreate(BaseModel):
    assessment_id: int
    administered_date: date
    raw_score: float | None = None
    scaled_score: float | None = None
    responses: dict | None = None
    observations: str | None = None
    administered_by: str


class AssessmentResultOut(AssessmentResultCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    created_at: datetime


class InterventionSave(BaseModel):
    risk_level: str
    intervention_type: str
    description: str
    assigned_to: str
    ai_recommendations: dict | None = None


class InterventionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    risk_level: str
    intervention_type: str
    description: str
    start_date: date
    end_date: date | None
    status: str
    assigned_to: str
    outcome_notes: str | None


# ── NICHQ Vanderbilt Teacher Informant intake ──────────────────────────────

class VanderbiltCoreSymptoms(BaseModel):
    """Anxiety/depression domain — 7 items, 0-3 each."""
    item1: int = Field(ge=0, le=3)
    item2: int = Field(ge=0, le=3)
    item3: int = Field(ge=0, le=3)
    item4: int = Field(ge=0, le=3)
    item5: int = Field(ge=0, le=3)
    item6: int = Field(ge=0, le=3)
    item7: int = Field(ge=0, le=3)


class VanderbiltClassroomPerformance(BaseModel):
    """5 items, 1-5 each."""
    academic_performance: int = Field(ge=1, le=5)
    classroom_behavioral_performance: int = Field(ge=1, le=5)
    peer_relationships: int = Field(ge=1, le=5)
    following_directions: int = Field(ge=1, le=5)
    disrupting_class: int = Field(ge=1, le=5)


class VanderbiltAttentionItems(BaseModel):
    items: list[int] = Field(min_length=9, max_length=9)


class VanderbiltHyperactivityItems(BaseModel):
    items: list[int] = Field(min_length=9, max_length=9)


class VanderbiltOppositionalConductItems(BaseModel):
    items: list[int] = Field(min_length=10, max_length=10)


class VanderbiltAcademicPerformance(BaseModel):
    items: list[int] = Field(min_length=3, max_length=3)


class VanderbiltExtendedSections(BaseModel):
    attention: VanderbiltAttentionItems | None = None
    hyperactivity_impulsivity: VanderbiltHyperactivityItems | None = None
    oppositional_conduct: VanderbiltOppositionalConductItems | None = None
    academic_performance: VanderbiltAcademicPerformance | None = None


class VanderbiltTeacherAssessmentCreate(BaseModel):
    teacher_name: str
    administered_date: date
    weeks_observed: int = Field(ge=0)
    concern_flags: list[str] = []
    anxiety_depression: VanderbiltCoreSymptoms
    classroom_behavioral: VanderbiltClassroomPerformance
    extended: VanderbiltExtendedSections | None = None
    comments: str | None = None
