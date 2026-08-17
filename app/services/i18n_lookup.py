"""DB-backed translation lookup — used by both GET /i18n/translations (for
the frontend dropdown) and app/services/intervention_report.py (for the
generated .docx's fixed labels). Single source of truth, replacing the old
project's two hardcoded JS I18N blobs and its intervention_report LABELS
dict."""
from sqlalchemy.orm import Session

from app.config import settings
from app.models.i18n import Language, Translation


def _resolve_language(lang_code: str | None, db: Session) -> Language:
    if lang_code:
        lang = db.query(Language).filter(Language.code == lang_code, Language.is_active.is_(True)).first()
        if lang:
            return lang
    default = db.query(Language).filter(Language.code == settings.default_language_code).first()
    if default:
        return default
    return db.query(Language).filter(Language.is_default.is_(True)).first()


def get_translations_dict(lang_code: str | None, db: Session) -> dict[str, str]:
    lang = _resolve_language(lang_code, db)
    if not lang:
        return {}
    rows = db.query(Translation.key, Translation.value).filter(Translation.language_id == lang.id).all()
    return {key: value for key, value in rows}


def get_translation(key: str, lang_code: str | None, db: Session, default: str = "") -> str:
    lang = _resolve_language(lang_code, db)
    if not lang:
        return default
    row = db.query(Translation.value).filter(Translation.language_id == lang.id, Translation.key == key).first()
    return row[0] if row else default


def get_language_display_name(lang_code: str | None, db: Session) -> str:
    """Resolves a language code (e.g. 'ms') to its display name (e.g. 'Bahasa
    Malaysia') for use in agent prompts — used by both risk assessment/
    intervention (app/api/risk.py) and referral (app/api/referrals.py)."""
    if lang_code:
        lang = db.query(Language).filter(Language.code == lang_code).first()
        if lang:
            return lang.name
    default = db.query(Language).filter(Language.code == settings.default_language_code).first()
    return default.name if default else "English"
