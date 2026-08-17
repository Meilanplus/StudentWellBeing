"""Optional demo cohort — run manually (`python seed_demo.py`), never
auto-executed on startup. Bootstraps one super_admin account (since nobody
can call POST /auth/register without an already-authenticated requester —
the very first account has to be inserted directly), plus a small set of
realistic students/attendance/behavior/assessment records so the four
agents have something to analyze. Idempotent."""
import random
from datetime import date, timedelta

from app.database import SessionLocal, init_db
from app.security import hash_password
from app.models.user import User
from app.models.rbac import Role
from app.models.geography import School
from app.models.student import Student, AttendanceRecord, BehaviorRecord
from app.models.assessment import Assessment, AssessmentResult
from app.constants import ROLE_SUPER_ADMIN

STUDENTS = [
    {"student_id": "SMK2026001", "full_name": "Ahmad Haziq bin Razali", "dob": date(2014, 3, 12), "gender": "Male", "class_name": "4A", "ses": "middle", "guardian": "Razali bin Ismail", "contact": "012-3456701", "profile": "low"},
    {"student_id": "SMK2026002", "full_name": "Lee Jia Hui", "dob": date(2014, 6, 2), "gender": "Female", "class_name": "4A", "ses": "high", "guardian": "Lee Wei Ming", "contact": "012-3456702", "profile": "low"},
    {"student_id": "SMK2026003", "full_name": "Rajesh a/l Subramaniam", "dob": date(2013, 11, 20), "gender": "Male", "class_name": "5B", "ses": "low", "guardian": "Subramaniam a/l Muthu", "contact": "012-3456703", "profile": "moderate"},
    {"student_id": "SMK2026004", "full_name": "Nur Aisyah binti Kamal", "dob": date(2013, 1, 9), "gender": "Female", "class_name": "5B", "ses": "middle", "guardian": "Kamal bin Hassan", "contact": "012-3456704", "profile": "high"},
    {"student_id": "SMK2026005", "full_name": "Tan Wei Jian", "dob": date(2012, 8, 30), "gender": "Male", "class_name": "6A", "ses": "middle", "guardian": "Tan Chee Keong", "contact": "012-3456705", "profile": "moderate"},
]


def _build_attendance(profile: str) -> list[dict]:
    today = date.today()
    records = []
    absence_prob = {"low": 0.03, "moderate": 0.15, "high": 0.32}[profile]
    for i in range(30):
        d = today - timedelta(days=i)
        if d.weekday() >= 5:
            continue
        status = "absent" if random.random() < absence_prob else "present"
        records.append({"record_date": d, "att_per": status, "reason": None, "recorded_by": "seed_demo"})
    return records


def _build_behavior(profile: str, student_id_ext: str) -> list[dict]:
    if profile == "low":
        return []
    if profile == "moderate":
        return [
            {"incident_date": date.today() - timedelta(days=10), "incident_type": "discipline", "severity": "moderate",
             "description": "Repeated lateness to class.", "action_taken": "Verbal warning given.", "reported_by": "seed_demo"},
        ]
    return [
        {"incident_date": date.today() - timedelta(days=5), "incident_type": "emotional", "severity": "serious",
         "description": "Withdrawn behavior, refused to participate in class activities, reported feeling isolated.",
         "action_taken": "Referred to class teacher for follow-up.", "reported_by": "seed_demo"},
        {"incident_date": date.today() - timedelta(days=20), "incident_type": "discipline", "severity": "serious",
         "description": "Altercation with a classmate during recess.", "action_taken": "Counseling session scheduled.", "reported_by": "seed_demo"},
    ]


def seed_demo():
    db = SessionLocal()
    try:
        school = db.query(School).first()
        if not school:
            raise RuntimeError("Run seed_geography.py first — no school found.")

        super_admin_role = db.query(Role).filter(Role.code == ROLE_SUPER_ADMIN).first()
        if not super_admin_role:
            raise RuntimeError("Run seed_rbac.py first — no super_admin role found.")

        if not db.query(User).filter(User.ic_number == "000000000001").first():
            db.add(User(
                ic_number="000000000001",
                name="System Administrator",
                role_id=super_admin_role.id,
                school_id=None,
                email="admin@example.edu.my",
                phone="012-0000000",
                hashed_password=hash_password("ChangeMe123!"),
            ))
            db.commit()
            print("Bootstrap super_admin created: IC 000000000001 / password ChangeMe123!")
        else:
            print("Bootstrap super_admin already exists.")

        assessment_defs = [
            {"name": "NICHQ Vanderbilt Assessment Scale", "instrument_type": "behavioral_screening",
             "scoring_guide": {"cutoff": 70}},
            {"name": "Saringan Minda Sihat (SMS)", "instrument_type": "mental_health_screening",
             "scoring_guide": {"scale": "0-30"}},
        ]
        assessments_by_name = {}
        for a_def in assessment_defs:
            a = db.query(Assessment).filter(Assessment.name == a_def["name"]).first()
            if not a:
                a = Assessment(**a_def)
                db.add(a)
                db.flush()
            assessments_by_name[a_def["name"]] = a
        db.commit()

        added = 0
        for s_def in STUDENTS:
            if db.query(Student).filter(Student.student_id == s_def["student_id"]).first():
                continue
            student = Student(
                student_id=s_def["student_id"],
                full_name=s_def["full_name"],
                date_of_birth=s_def["dob"],
                gender=s_def["gender"],
                class_name=s_def["class_name"],
                school_year=date.today().year,
                school_id=school.id,
                socioeconomic_status=s_def["ses"],
                guardian_name=s_def["guardian"],
                guardian_contact=s_def["contact"],
            )
            db.add(student)
            db.flush()

            for att in _build_attendance(s_def["profile"]):
                db.add(AttendanceRecord(student_id=student.id, **att))
            for beh in _build_behavior(s_def["profile"], s_def["student_id"]):
                db.add(BehaviorRecord(student_id=student.id, **beh))

            scaled_score = {"low": 20.0, "moderate": 48.0, "high": 78.0}[s_def["profile"]]
            db.add(AssessmentResult(
                student_id=student.id,
                assessment_id=assessments_by_name["Saringan Minda Sihat (SMS)"].id,
                administered_date=date.today() - timedelta(days=7),
                raw_score=scaled_score,
                scaled_score=scaled_score,
                observations=f"Seeded {s_def['profile']}-risk profile for demo purposes.",
                administered_by="seed_demo",
            ))
            added += 1

        db.commit()
        print(f"Seeded {added} new demo students (of {len(STUDENTS)} defined) under school '{school.name}'.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_demo()
