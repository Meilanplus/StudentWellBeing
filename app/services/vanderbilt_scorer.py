"""NICHQ Vanderbilt Teacher Informant scoring — a domain is a "positive
screen" only if it meets BOTH the symptom-count threshold AND a performance
impairment is present (matching the real instrument's requirement that
symptoms co-occur with functional impairment, not just be present)."""
from app.schemas.assessment import VanderbiltTeacherAssessmentCreate

# domain -> (positive_count_threshold, item_count)
DOMAIN_THRESHOLDS = {
    "attention": (6, 9),
    "hyperactivity_impulsivity": (6, 9),
    "oppositional_conduct": (3, 10),
    "anxiety_depression": (3, 7),
}

SYMPTOM_ITEM_SCALE_MAX = 3  # each symptom item is scored 0-3
POSITIVE_ITEM_THRESHOLD = 2  # items scored >=2 count toward "positive"
PERFORMANCE_IMPAIRMENT_THRESHOLD = 4  # performance items scored 1-5; 4-5 = impairment


def _positive_count(items: list[int]) -> int:
    return sum(1 for v in items if v >= POSITIVE_ITEM_THRESHOLD)


def score_teacher_assessment(payload: VanderbiltTeacherAssessmentCreate) -> dict:
    anxiety_items = list(payload.anxiety_depression.model_dump().values())
    performance_items = list(payload.classroom_behavioral.model_dump().values())

    domain_raw_items: dict[str, list[int]] = {"anxiety_depression": anxiety_items}
    if payload.extended:
        if payload.extended.attention:
            domain_raw_items["attention"] = payload.extended.attention.items
        if payload.extended.hyperactivity_impulsivity:
            domain_raw_items["hyperactivity_impulsivity"] = payload.extended.hyperactivity_impulsivity.items
        if payload.extended.oppositional_conduct:
            domain_raw_items["oppositional_conduct"] = payload.extended.oppositional_conduct.items
        if payload.extended.academic_performance:
            performance_items += payload.extended.academic_performance.items

    performance_impairment = any(v >= PERFORMANCE_IMPAIRMENT_THRESHOLD for v in performance_items)
    average_performance_score = round(sum(performance_items) / len(performance_items), 2) if performance_items else None

    domain_screens = {}
    total_raw = 0
    total_max = 0
    positive_screen_domains = []
    for domain, items in domain_raw_items.items():
        threshold, expected_count = DOMAIN_THRESHOLDS[domain]
        positive_count = _positive_count(items)
        is_positive = positive_count >= threshold and performance_impairment
        domain_screens[domain] = {
            "positive_count": positive_count,
            "threshold": threshold,
            "item_count": len(items),
            "positive_screen": is_positive,
        }
        if is_positive:
            positive_screen_domains.append(domain)
        total_raw += sum(items)
        total_max += len(items) * SYMPTOM_ITEM_SCALE_MAX

    concern_score = (total_raw / total_max * 100) if total_max else 0.0
    if performance_impairment:
        concern_score = min(concern_score + 10, 100)

    return {
        "average_performance_score": average_performance_score,
        "performance_impairment": performance_impairment,
        "domain_screens": domain_screens,
        "positive_screen_domains": positive_screen_domains,
        "total_symptom_raw_score": total_raw,
        "concern_score_0_100": round(concern_score, 1),
    }
