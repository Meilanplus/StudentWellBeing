"""Builds the downloadable School-Based Intervention Plan .docx from an
InterventionRecommendation (Agent 2's output). Built programmatically with
python-docx (no external template dependency) so a fresh project doesn't
need a matching .docx template shipped alongside it. Fixed headings/labels
come from the DB-backed translations table (app/services/i18n_lookup.py)
instead of a hardcoded LABELS dict, keyed by the same language code used
elsewhere in the app."""
import io

from docx import Document
from docx.shared import Pt, RGBColor
from sqlalchemy.orm import Session

from app.schemas.risk import InterventionRecommendation
from app.services.i18n_lookup import get_translation

STRATEGY_AREAS = ["Classroom", "Instruction", "Differentiated Learning", "Behaviour", "Movement", "Counselling", "Parents"]

_HEADER_BLUE = RGBColor(0x1A, 0x3A, 0xAD)


def _label(key: str, lang_code: str, db: Session, default: str) -> str:
    return get_translation(key, lang_code, db, default=default)


def _add_heading(doc: Document, text: str) -> None:
    h = doc.add_heading(text, level=1)
    for run in h.runs:
        run.font.color.rgb = _HEADER_BLUE


def _add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def generate_intervention_docx(plan: InterventionRecommendation, lang_code: str, db: Session) -> bytes:
    doc = Document()

    title = _label("report.school_based_intervention_plan", lang_code, db, "School-Based Intervention Plan")
    heading = doc.add_heading(title, level=0)
    for run in heading.runs:
        run.font.color.rgb = _HEADER_BLUE

    disclaimer_p = doc.add_paragraph(plan.disclaimer)
    disclaimer_p.runs[0].italic = True
    disclaimer_p.runs[0].font.size = Pt(9)

    _add_heading(doc, _label("intervention.student_information", lang_code, db, "Student Information"))
    info_table = doc.add_table(rows=0, cols=2)
    info_table.style = "Light Grid Accent 1"
    for label, value in [
        (_label("common.student_name", lang_code, db, "Student Name"), plan.student_name),
        (_label("common.class", lang_code, db, "Class"), plan.class_name),
        (_label("common.age", lang_code, db, "Age"), str(plan.age) if plan.age is not None else "-"),
        (_label("common.risk_level", lang_code, db, "Risk Level"), plan.risk_level),
        (_label("common.school", lang_code, db, "School"), plan.school_name),
        (_label("common.case_reference", lang_code, db, "Case Reference"), plan.case_reference),
        (_label("common.prepared_by", lang_code, db, "Prepared by"), plan.prepared_by),
        (_label("common.date", lang_code, db, "Date"), plan.date),
    ]:
        row = info_table.add_row().cells
        row[0].text = label
        row[1].text = value

    _add_heading(doc, _label("intervention.reason_for_intervention", lang_code, db, "Reason for Intervention"))
    _add_bullets(doc, plan.reason_for_intervention)

    _add_heading(doc, _label("intervention.objectives", lang_code, db, "Intervention Objectives"))
    _add_bullets(doc, plan.intervention_objectives)

    _add_heading(doc, _label("intervention.ai_recommended_plan", lang_code, db, "AI Recommended Intervention Plan"))
    strategy_table = doc.add_table(rows=1, cols=5)
    strategy_table.style = "Light Grid Accent 1"
    header_cells = strategy_table.rows[0].cells
    columns = [
        _label("intervention.area", lang_code, db, "Area"),
        _label("intervention.strategy_col", lang_code, db, "Strategy"),
        _label("intervention.responsible_person", lang_code, db, "Responsible Person"),
        _label("intervention.frequency", lang_code, db, "Frequency"),
        _label("intervention.success_indicator", lang_code, db, "Success Indicator"),
    ]
    for i, col in enumerate(columns):
        header_cells[i].text = col
    by_area = {s.area: s for s in plan.strategies}
    for area in STRATEGY_AREAS:
        s = by_area.get(area)
        row = strategy_table.add_row().cells
        row[0].text = area
        row[1].text = s.strategy if s else "-"
        row[2].text = s.responsible if s else "-"
        row[3].text = s.frequency if s else "-"
        row[4].text = s.success_indicator if s else "-"

    _add_heading(doc, _label("intervention.recommended_tools", lang_code, db, "Recommended Tools"))
    _add_bullets(doc, plan.recommended_tools)

    _add_heading(doc, _label("intervention.parent_support_guide", lang_code, db, "Parent Support Guide"))
    _add_bullets(doc, plan.home_strategies)

    _add_heading(doc, _label("intervention.expected_outcomes", lang_code, db, "Expected Outcomes"))
    _add_bullets(doc, plan.expected_outcomes)

    _add_heading(doc, _label("intervention.monitoring_checklist", lang_code, db, "Monitoring Checklist"))
    _add_bullets(doc, plan.monitoring_checklist)

    _add_heading(doc, _label("intervention.counselor_recommendation", lang_code, db, "Counselor Recommendation"))
    doc.add_paragraph(plan.counselor_recommendation)

    if plan.referral_recommended:
        _add_heading(doc, _label("intervention.referral_recommendation_heading", lang_code, db, "Referral Recommendation"))
        doc.add_paragraph(plan.referral_reason or _label("intervention.referral_to_agent3_default", lang_code, db, "Referral to Agent 3 recommended."))

    _add_heading(doc, _label("intervention.action_items", lang_code, db, "Action Items"))
    doc.add_paragraph(_label("common.teacher", lang_code, db, "Teacher") + ":", style="Intense Quote")
    _add_bullets(doc, plan.action_items_teacher)
    doc.add_paragraph(_label("common.counselor", lang_code, db, "Counselor") + ":", style="Intense Quote")
    _add_bullets(doc, plan.action_items_counselor)
    doc.add_paragraph(_label("common.parent", lang_code, db, "Parent") + ":", style="Intense Quote")
    _add_bullets(doc, plan.action_items_parent)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
