"""Task-based permission system, backed by the roles/tasks/role_tasks tables
(app/models/rbac.py) instead of the old project's hardcoded Python dict.

Task IDs/labels/registration pairing rules are still defined once in
app/constants.py (single source of truth for what the matrix *should* be —
seed_rbac.py loads that into the DB); this module only ever reads the DB, so
an admin could in principle re-point a role's tasks without a code change.
"""
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from app.database import get_db
from app.security import get_current_user
from app.models.user import User
from app.models.rbac import Role, Task, RoleTask
from app.constants import (
    REGISTRATION_TASK_BY_ROLE,
    REGISTRATION_TASKS,
    ANY_SCHOOL_TASKS,
)


def get_role_task_ids(role_id: int, db: Session) -> set[int]:
    rows = db.query(RoleTask.task_id).filter(RoleTask.role_id == role_id).all()
    return {row[0] for row in rows}


def _task_labels(task_ids: tuple[int, ...], db: Session) -> str:
    rows = db.query(Task.label).filter(Task.id.in_(task_ids)).all()
    return ", ".join(row[0] for row in rows)


def is_manager(role_id: int, db: Session) -> bool:
    """True if this role holds at least one registration task."""
    return bool(get_role_task_ids(role_id, db) & REGISTRATION_TASKS)


def is_school_scoped_manager(role_id: int, db: Session) -> bool:
    """True if this role can manage users only within its own school."""
    tasks = get_role_task_ids(role_id, db)
    return bool(tasks & REGISTRATION_TASKS) and not (tasks & ANY_SCHOOL_TASKS)


def require_task(*task_ids: int):
    """FastAPI dependency factory. Resolves the caller from the JWT (see
    app/security.py), 403s unless their role holds at least one of the given
    tasks. Returns the User so the route can use it (e.g. for defaults like
    `prepared_by`)."""

    def dependency(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        allowed = get_role_task_ids(user.role_id, db)
        if not allowed.intersection(task_ids):
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user.role.code}' is not permitted to: {_task_labels(task_ids, db)}.",
            )
        return user

    return dependency


def require_manager(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    if not is_manager(user.role_id, db):
        raise HTTPException(status_code=403, detail="This role has no user-management tasks.")
    return user


def check_can_register_role(requester: User, target_role_code: str, target_school_id: int | None, db: Session) -> None:
    """Enforces the registration task pairs (5/6, 7/8, 10/11, 12/13) for
    assigning `target_role_code` to a user at `target_school_id`."""
    pair = REGISTRATION_TASK_BY_ROLE.get(target_role_code)
    if not pair:
        raise HTTPException(
            status_code=403,
            detail=f"No task permits registering or assigning the role '{target_role_code}'.",
        )
    one_school_task, any_school_task = pair
    requester_tasks = get_role_task_ids(requester.role_id, db)

    if any_school_task in requester_tasks:
        return
    if one_school_task in requester_tasks and target_school_id == requester.school_id:
        return

    raise HTTPException(
        status_code=403,
        detail=f"Role '{requester.role.code}' is not authorized to register/assign role '{target_role_code}' for this school.",
    )
