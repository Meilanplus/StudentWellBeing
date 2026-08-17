from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Dev-convenience fallback (create_all). Production schema changes go
    through Alembic migrations (`alembic upgrade head`) instead."""
    from app.models import student, assessment, intervention, user, geography, rbac, i18n, character_category  # noqa: F401

    Base.metadata.create_all(bind=engine)
