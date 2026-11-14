from datetime import UTC, date, datetime, timedelta
from typing import Literal

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from app.api.deps import CurrentCouple, CurrentUser
from app.database import DbSession
from app.enums import TaskCategory
from app.models import Couple, Task
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/couple/tasks", tags=["tasks"])


def get_couple_task(task_id: int, couple: Couple, db: DbSession) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.couple_id != couple.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def check_assignee(assignee_id: int | None, couple: Couple) -> None:
    if assignee_id is not None and assignee_id not in {m.id for m in couple.members}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="assignee_id must be a member of your couple",
        )


@router.get("", response_model=list[TaskRead])
def list_tasks(
    user: CurrentUser,
    couple: CurrentCouple,
    db: DbSession,
    is_done: bool | None = None,
    for_me: bool = False,
    due: Literal["overdue", "today", "week"] | None = None,
    category: TaskCategory | None = None,
) -> list[Task]:
    """Not done first, then the nearest due date; tasks without a date go last.

    - for_me: only tasks assigned to me or to both of us
    - due: overdue / today / week (today and the next 7 days)
    """
    stmt = select(Task).where(Task.couple_id == couple.id)
    if is_done is not None:
        stmt = stmt.where(Task.is_done == is_done)
    if for_me:
        stmt = stmt.where(or_(Task.assignee_id == user.id, Task.assignee_id.is_(None)))
    if category is not None:
        stmt = stmt.where(Task.category == category)
    today = date.today()
    if due == "overdue":
        stmt = stmt.where(Task.due_date < today, Task.is_done.is_(False))
    elif due == "today":
        stmt = stmt.where(Task.due_date == today)
    elif due == "week":
        stmt = stmt.where(Task.due_date.between(today, today + timedelta(days=7)))
    stmt = stmt.order_by(
        Task.is_done, Task.due_date.is_(None), Task.due_date, Task.created_at.desc(), Task.id.desc()
    )
    return list(db.scalars(stmt))


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, user: CurrentUser, couple: CurrentCouple, db: DbSession) -> Task:
    check_assignee(data.assignee_id, couple)
    task = Task(**data.model_dump(), couple=couple, author_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskRead)
def read_task(task_id: int, couple: CurrentCouple, db: DbSession) -> Task:
    return get_couple_task(task_id, couple, db)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, data: TaskUpdate, couple: CurrentCouple, db: DbSession) -> Task:
    task = get_couple_task(task_id, couple, db)
    changes = data.model_dump(exclude_unset=True)
    if "assignee_id" in changes:
        check_assignee(changes["assignee_id"], couple)
    for field, value in changes.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, couple: CurrentCouple, db: DbSession) -> None:
    db.delete(get_couple_task(task_id, couple, db))
    db.commit()


@router.post("/{task_id}/done", response_model=TaskRead)
def mark_done(task_id: int, user: CurrentUser, couple: CurrentCouple, db: DbSession) -> Task:
    task = get_couple_task(task_id, couple, db)
    task.is_done = True
    task.done_at = datetime.now(UTC)
    task.done_by_id = user.id
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/undone", response_model=TaskRead)
def mark_undone(task_id: int, couple: CurrentCouple, db: DbSession) -> Task:
    task = get_couple_task(task_id, couple, db)
    task.is_done = False
    task.done_at = task.done_by_id = None
    db.commit()
    db.refresh(task)
    return task
