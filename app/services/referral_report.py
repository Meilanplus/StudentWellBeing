"""Builds the downloadable Referral Letter .docx from a ReferralDocument
(Agent 3's output). Mirrors intervention_report.py's approach: built
programmatically with python-docx, fixed headings pulled from the DB-backed
translations table."""
import io
import re

from docx import Document
from docx.shared import Pt, RGBColor
from sqlalchemy.orm import Session

from app.schemas.risk import ReferralDocument
from app.services.i18n_lookup import get_translation

_HEADER_BLUE = RGBColor(0x1A, 0x3A, 0xAD)
_BULLET_RE = re.compile(r"^[-*•]\s+(.*)$")


def _label(key: str, lang_code: str, db: Session, default: str) -> str:
    return get_translation(key, lang_code, db, default=default)


def _add_heading(doc: Document, text: str) -> None:
    h = doc.add_heading(text, level=1)
    for run in h.runs:
        run.font.color.rgb = _HEADER_BLUE


def _add_supporting_summary(doc: Document, text: str) -> None:
    """Agent 3 writes this as section headers followed by "- " bulleted
    lines (see referral_agent.py's system prompt) — same structure the web
    view parses in renderSupportingSummary(), mirrored here."""
    for raw_line in (text or "").split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        bullet_match = _BULLET_RE.match(line)
        if bullet_match:
            doc.add_paragraph(bullet_match.group(1), style="List Bullet")
        else:
            h = doc.add_heading(line, level=2)
            for run in h.runs:
                run.font.color.rgb = _HEADER_BLUE


def generate_referral_docx(referral: ReferralDocument, lang_code: str, db: Session) -> bytes:
    doc = Document()

    title = _label("referral.letter_title", lang_code, db, "Referral Letter")
    heading = doc.add_heading(title, level=0)
    for run in heading.runs:
        run.font.color.rgb = _HEADER_BLUE

    disclaimer_p = doc.add_paragraph(referral.disclaimer)
    disclaimer_p.runs[0].italic = True
    disclaimer_p.runs[0].font.size = Pt(9)

    _add_heading(doc, "Referral Information")
    info_table = doc.add_table(rows=0, cols=2)
    info_table.style = "Light Grid Accent 1"
    for label, value in [
        ("Student Name", referral.student_name),
        ("Referral Type", referral.referral_type),
        ("Referred To", referral.referral_to),
        ("Prepared By", referral.prepared_by),
    ]:
        row = info_table.add_row().cells
        row[0].text = label
        row[1].text = value or "-"

    _add_heading(doc, "Referral Letter")
    for paragraph in referral.letter_content.split("\n"):
        if paragraph.strip():
            doc.add_paragraph(paragraph.strip())

    _add_heading(doc, "Supporting Summary")
    _add_supporting_summary(doc, referral.supporting_summary)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
