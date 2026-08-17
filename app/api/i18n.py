from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.i18n import Language
from app.schemas.i18n import LanguageOut
from app.services.i18n_lookup import get_translations_dict

router = APIRouter(prefix="/i18n", tags=["Multi-lingual"])


@router.get("/languages", response_model=list[LanguageOut])
def list_languages(db: Session = Depends(get_db)):
    return db.query(Language).filter(Language.is_active.is_(True)).order_by(Language.id).all()


@router.get("/translations")
def get_translations(lang: str, db: Session = Depends(get_db)) -> dict[str, str]:
    return get_translations_dict(lang, db)
