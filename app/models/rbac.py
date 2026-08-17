"""DB-backed role/task permission matrix (the 6-role x 16-task table).

Replaces the old project's hardcoded Python dicts (app/permissions.py's
ROLE_TASKS) with real tables, seeded by seed_rbac.py from the source
Roles-and-Tasks matrix. app/permissions.py still exposes the same
require_task() dependency shape, but backed by these tables (cached).
"""
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    role_tasks: Mapped[list["RoleTask"]] = relationship(back_populates="role", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)  # matches the S.No in the source matrix (1-16)
    code: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)

    role_tasks: Mapped[list["RoleTask"]] = relationship(back_populates="task", cascade="all, delete-orphan")


class RoleTask(Base):
    __tablename__ = "role_tasks"
    __table_args__ = (UniqueConstraint("role_id", "task_id", name="uq_role_task"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)

    role: Mapped["Role"] = relationship(back_populates="role_tasks")
    task: Mapped["Task"] = relationship(back_populates="role_tasks")
