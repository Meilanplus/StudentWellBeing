"""Seeds the state -> district -> school cascade (same starting cohort as
the old project: Wilayah Persekutuan Kuala Lumpur). Idempotent."""
from app.database import SessionLocal, init_db
from app.models.geography import State, District, School


def seed_geography():
    db = SessionLocal()
    try:
        state = db.query(State).filter(State.name == "Wilayah Persekutuan Kuala Lumpur").first()
        if not state:
            state = State(name="Wilayah Persekutuan Kuala Lumpur")
            db.add(state)
            db.flush()

        district_names = ["Keramat", "Sentul", "Pudu Bangsar"]
        districts = {}
        for name in district_names:
            d = db.query(District).filter(District.state_id == state.id, District.name == name).first()
            if not d:
                d = District(state_id=state.id, name=name)
                db.add(d)
                db.flush()
            districts[name] = d

        school_names = ["SK La Salle", "SJKC Sentul", "SJKT Sentul"]
        for name in school_names:
            s = db.query(School).filter(School.district_id == districts["Sentul"].id, School.name == name).first()
            if not s:
                db.add(School(district_id=districts["Sentul"].id, name=name))

        db.commit()
        print("Geography seeded: 1 state, 3 districts, 3 schools (idempotent).")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_geography()
