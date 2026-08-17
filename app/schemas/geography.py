from pydantic import BaseModel, ConfigDict


class StateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class DistrictOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    state_id: int
    name: str


class SchoolOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    district_id: int
    name: str
