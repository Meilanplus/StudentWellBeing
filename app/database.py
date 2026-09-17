import sys

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

def _normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def resolve_database_url() -> str:
    configured_url = _normalize_database_url(settings.database_url)
    fallback_url = _normalize_database_url(
        settings.fallback_database_url or "sqlite:///./studentwellbeing.db"
    )

    if not configured_url.startswith("postgresql+psycopg://"):
        return configured_url

    if str(settings.app_env).lower() == "production":
        return configured_url

    try:
        test_engine = create_engine(configured_url, pool_pre_ping=True, connect_args={"connect_timeout": 2})
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return configured_url
    except Exception:
        print(
            "Primary Postgres database is unavailable; falling back to the configured "
            "local development database for this startup.",
            file=sys.stderr,
        )
        return fallback_url


database_url = resolve_database_url()
engine = create_engine(database_url, pool_pre_ping=True)
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
    from app.models import (
        assessment,
        character_category,
        geography,
        i18n,
        intervention,
        rbac,
        student,
        user,
    )  # noqa: F401

    Base.metadata.create_all(bind=engine)
