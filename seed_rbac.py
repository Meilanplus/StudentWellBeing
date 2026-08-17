"""Seeds roles, tasks, and role_tasks exactly per the source Roles-and-Tasks
matrix (app/constants.py is the single source of truth for the numbers).
Idempotent: safe to re-run, upserts rather than duplicating rows."""
from app.database import SessionLocal, init_db
from app.models.rbac import Role, Task, RoleTask
from app.constants import ALL_ROLES, ROLE_NAMES, TASK_CODES, TASK_LABELS, ROLE_TASKS


def seed_rbac():
    db = SessionLocal()
    try:
        role_by_code = {r.code: r for r in db.query(Role).all()}
        for code in ALL_ROLES:
            role = role_by_code.get(code)
            if role is None:
                role = Role(code=code, name=ROLE_NAMES[code])
                db.add(role)
                db.flush()
                role_by_code[code] = role
            else:
                role.name = ROLE_NAMES[code]

        task_by_id = {t.id: t for t in db.query(Task).all()}
        for task_id, code in TASK_CODES.items():
            task = task_by_id.get(task_id)
            if task is None:
                task = Task(id=task_id, code=code, label=TASK_LABELS[task_id])
                db.add(task)
                db.flush()
                task_by_id[task_id] = task
            else:
                task.code = code
                task.label = TASK_LABELS[task_id]

        db.commit()

        existing_pairs = {(rt.role_id, rt.task_id) for rt in db.query(RoleTask).all()}
        added = 0
        for role_code, task_ids in ROLE_TASKS.items():
            role = role_by_code[role_code]
            for task_id in task_ids:
                if (role.id, task_id) not in existing_pairs:
                    db.add(RoleTask(role_id=role.id, task_id=task_id))
                    added += 1
        db.commit()
        print(f"Seeded {len(ALL_ROLES)} roles, {len(TASK_CODES)} tasks, {added} new role-task links.")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_rbac()
