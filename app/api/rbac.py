"""Read-only transparency into the DB-driven permission matrix — lets an
admin (or this project's own tests) confirm the seeded roles/tasks match the
source Roles-and-Tasks image exactly."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.rbac import Role, Task, RoleTask
from app.schemas.rbac import RoleOut, TaskOut, RoleMatrixEntry

router = APIRouter(prefix="/rbac", tags=["RBAC"])


@router.get("/roles", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).order_by(Role.id).all()


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.id).all()


@router.get("/matrix", response_model=list[RoleMatrixEntry])
def role_task_matrix(db: Session = Depends(get_db)):
    roles = db.query(Role).order_by(Role.id).all()
    entries = []
    for role in roles:
        task_ids = [rt.task_id for rt in db.query(RoleTask).filter(RoleTask.role_id == role.id).all()]
        tasks = db.query(Task).filter(Task.id.in_(task_ids)).order_by(Task.id).all()
        entries.append(RoleMatrixEntry(role=role, tasks=tasks))
    return entries
