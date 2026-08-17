"""Rule-based pre-screening — fast, free, no AI call. Gates whether the
expensive Agent 1 (LLM) call is even worth making: routine, low-signal
students skip straight to a canned "Low Risk" response (see app/api/risk.py).

Weighted multi-signal formula: Attendance 35% / NICHQ Vanderbilt 25% /
Discipline 20% / Emotional (GAD-2 + Whooley) 20%. Each signal is normalized
to a 0-100 sub-score independently; missing signals are excluded and the
remaining weights renormalized to 100%, rather than defaulting a missing
signal to 0 (which would silently read as "no risk")."""
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.student import AttendanceRecord, BehaviorRecord, MentalHealthRecord
from app.models.assessment import Assessment, AssessmentResult

SIGNAL_WEIGHTS = {
    "attendance": 0.35,
    "vanderbilt": 0.25,
    "discipline": 0.20,
    "emotional": 0.20,
}


def score_attendance_percentage(att_per: str) -> int:
    """Map an attendance percentage (e.g. '95%') to the school's 0-5 severity
    score: 91-100=0, 86-90=1, 81-85=2, 76-80=3, 71-75=4, below 70=5."""
    pct = float(att_per.strip().rstrip("%"))
    if pct >= 91:
        return 0
    if pct >= 86:
        return 1
    if pct >= 81:
        return 2
    if pct >= 76:
        return 3
    if pct >= 71:
        return 4
    return 5


def normalize_severity(severity: str) -> str:
    """Maps a behavior severity value — English or the Bahasa Melayu values
    actually entered (Ringan/Sederhana/Berat) — to serious/moderate/minor.
    Unrecognized values default to moderate rather than being silently ignored."""
    key = severity.strip().lower()
    if key in ("serious", "berat"):
        return "serious"
    if key in ("minor", "ringan"):
        return "minor"
    return "moderate"


SEVERITY_BASE_POINTS = {"serious": 90, "moderate": 55, "minor": 20}


def _score_attendance(student_db_id: int, db: Session, today: date, flags: list[str]) -> float | None:
    since_30 = today - timedelta(days=30)
    attendance = (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.student_id == student_db_id, AttendanceRecord.record_date >= since_30)
        .all()
    )
    if not attendance:
        return None

    att_scores = [score_attendance_percentage(a.att_per) for a in attendance]
    avg_band = sum(att_scores) / len(att_scores)
    subscore = avg_band / 5 * 100
    if avg_band >= 4:
        flags.append("Very low attendance (30-day)")
    elif avg_band >= 3:
        flags.append("Low attendance (30-day)")
    elif avg_band >= 1:
        flags.append("Below-target attendance (30-day)")

    since_14 = today - timedelta(days=14)
    recent = [s for a, s in zip(attendance, att_scores) if a.record_date >= since_14]
    prior = [s for a, s in zip(attendance, att_scores) if a.record_date < since_14]
    if len(recent) >= 3 and len(prior) >= 3:
        recent_avg = sum(recent) / len(recent)
        prior_avg = sum(prior) / len(prior)
        if recent_avg > prior_avg + 1:
            flags.append("Sudden drop in attendance")

    return subscore


def _score_vanderbilt(student_db_id: int, db: Session, flags: list[str]) -> float | None:
    latest = (
        db.query(AssessmentResult)
        .join(Assessment, AssessmentResult.assessment_id == Assessment.id)
        .filter(AssessmentResult.student_id == student_db_id, Assessment.name.ilike("%vanderbilt%"))
        .order_by(AssessmentResult.administered_date.desc())
        .first()
    )
    if not latest or latest.scaled_score is None:
        return None

    subscore = latest.scaled_score
    if subscore >= 70:
        flags.append("High concern score on latest NICHQ Vanderbilt assessment")
    elif subscore >= 50:
        flags.append("Elevated concern score on latest NICHQ Vanderbilt assessment")
    return subscore


def _score_discipline(student_db_id: int, db: Session, today: date, flags: list[str]) -> float:
    since_90 = today - timedelta(days=90)
    behavior = (
        db.query(BehaviorRecord)
        .filter(BehaviorRecord.student_id == student_db_id, BehaviorRecord.incident_date >= since_90)
        .all()
    )
    if not behavior:
        return 0.0

    levels = [normalize_severity(b.severity) for b in behavior]
    base = max(SEVERITY_BASE_POINTS[lvl] for lvl in levels)
    repeat_count = sum(1 for lvl in levels if lvl in ("serious", "moderate"))
    subscore = min(100.0, base + 10 * max(0, repeat_count - 1))

    if "serious" in levels and repeat_count >= 2:
        flags.append("Multiple serious/moderate behavior incidents (90-day)")
    elif "serious" in levels:
        flags.append("A serious behavior incident (90-day)")
    elif repeat_count >= 3:
        flags.append("Repeated moderate behavior incidents (90-day)")
    return subscore


def score_emotional_record(gad2_score: int, whooley: str) -> float:
    """Combines GAD-2 (continuous, 0-9) and Whooley (categorical) rather than
    trusting either single-timepoint self-report screen alone."""
    gad2_subscore = gad2_score / 9 * 100
    whooley_subscore = 100.0 if whooley.strip().lower() == "positive" else 0.0
    return min(100.0, gad2_subscore * 0.7 + whooley_subscore * 0.3)


def _score_emotional(student_db_id: int, db: Session, flags: list[str]) -> float | None:
    records = (
        db.query(MentalHealthRecord)
        .filter(MentalHealthRecord.student_id == student_db_id)
        .order_by(MentalHealthRecord.year.desc(), MentalHealthRecord.semester.desc())
        .limit(2)
        .all()
    )
    if not records:
        return None

    latest = records[0]
    subscore = score_emotional_record(latest.gad2_score, latest.whooley)
    if subscore >= 70:
        flags.append("High concern on latest emotional screening (GAD-2/Whooley)")
    elif subscore >= 50:
        flags.append("Elevated concern on latest emotional screening (GAD-2/Whooley)")

    if len(records) == 2:
        previous_subscore = score_emotional_record(records[1].gad2_score, records[1].whooley)
        if subscore > previous_subscore + 15:
            flags.append("Worsening emotional score trend")

    return subscore


def compute_pre_screen_detail(student_db_id: int, db: Session) -> dict:
    today = date.today()
    flags: list[str] = []

    breakdown = {
        "attendance": _score_attendance(student_db_id, db, today, flags),
        "vanderbilt": _score_vanderbilt(student_db_id, db, flags),
        "discipline": _score_discipline(student_db_id, db, today, flags),
        "emotional": _score_emotional(student_db_id, db, flags),
    }

    present = {name: sub for name, sub in breakdown.items() if sub is not None}
    missing = [name for name in breakdown if name not in present]
    for name in missing:
        flags.append(f"No {name} data on record — score based on {len(present)} of {len(breakdown)} signals only")

    if not present:
        return {
            "score": 0,
            "flags": ["No data available for risk assessment"],
            "breakdown": {name: {"subscore": None, "weight": w, "present": False} for name, w in SIGNAL_WEIGHTS.items()},
        }

    total_weight = sum(SIGNAL_WEIGHTS[name] for name in present)
    weighted_sum = sum(SIGNAL_WEIGHTS[name] * sub for name, sub in present.items())
    score = round(min(100.0, weighted_sum / total_weight))

    return {
        "score": score,
        "flags": flags,
        "breakdown": {
            name: {
                "subscore": breakdown[name],
                "weight": SIGNAL_WEIGHTS[name],
                "present": name in present,
            }
            for name in SIGNAL_WEIGHTS
        },
    }


def compute_pre_screen_score(student_db_id: int, db: Session) -> tuple[int, list[str]]:
    detail = compute_pre_screen_detail(student_db_id, db)
    return detail["score"], detail["flags"]
