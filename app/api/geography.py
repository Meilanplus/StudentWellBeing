from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.geography import State, District, School
from app.schemas.geography import StateOut, DistrictOut, SchoolOut

router = APIRouter(prefix="/geography", tags=["Geography"])


@router.get("/states", response_model=list[StateOut])
def list_states(db: Session = Depends(get_db)):
    return db.query(State).order_by(State.name).all()


@router.get("/districts", response_model=list[DistrictOut])
def list_districts(state_id: int, db: Session = Depends(get_db)):
    return db.query(District).filter(District.state_id == state_id).order_by(District.name).all()


@router.get("/schools", response_model=list[SchoolOut])
def list_schools(district_id: int, db: Session = Depends(get_db)):
    return db.query(School).filter(School.district_id == district_id).order_by(School.name).all()
