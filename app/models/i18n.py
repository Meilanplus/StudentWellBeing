"""DB-backed multi-lingual support: languages available in the dropdown and
the translation strings the frontend/i18n_lookup service resolve at runtime."""
from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Language(Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)  # en, ms, zh, ta
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # English display name
    native_name: Mapped[str] = mapped_column(String(50), nullable=False)  # name in that language
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    translations: Mapped[list["Translation"]] = relationship(back_populates="language", cascade="all, delete-orphan")


class Translation(Base):
    __tablename__ = "translations"
    __table_args__ = (UniqueConstraint("language_id", "key", name="uq_translation_language_key"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    language_id: Mapped[int] = mapped_column(ForeignKey("languages.id"), nullable=False)
    key: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    value: Mapped[str] = mapped_column(String, nullable=False)

    language: Mapped["Language"] = relationship(back_populates="translations")
