from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, get_current_user
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate, ListingTasks

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
        task_in: TaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> Task:
    task_to_create = task_in.model_dump()
    task_to_create["user_id"] = current_user.id
    task_data = Task(**task_to_create)
    db.add(task_data)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already exists"
        )
    db.refresh(task_data)
    return task_data


@router.get("/", response_model=ListingTasks, status_code=status.HTTP_200_OK)
def read_tasks(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
        is_done: bool | None = None,
        due_before: datetime | None = None,
        due_after: datetime | None = None,
        offset: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
) -> ListingTasks:
    tasks =db.query(Task).filter(Task.user_id == current_user.id)

    if is_done is not None:
        tasks = tasks.filter(Task.is_done == is_done)

    if due_before and due_after and due_after > due_before:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Date contradiction"
        )

    if due_before is not None:
        tasks = tasks.filter(Task.due_at <= due_before)

    if due_after is not None:
        tasks = tasks.filter(Task.due_at >= due_after)

    total = tasks.count()
    items = tasks.order_by(Task.due_at.desc(), Task.id.desc()).offset(offset).limit(limit).all()

    return ListingTasks(
        items=items,
        total=total,
        offset=offset,
        limit=limit,
        has_more=True if total > offset + limit else False,
    )


@router.get("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
def read_a_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db))-> TaskOut:
    current_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).one_or_none()
    if not current_task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    return current_task


@router.patch("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
def update_task(updates: TaskUpdate, task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> TaskOut:
    task_to_update = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).one_or_none()
    if not task_to_update:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    task_data = updates.model_dump(exclude_none=True)
    for field, value in task_data.items():
        setattr(task_to_update, field, value)
    db.commit()
    db.refresh(task_to_update)
    return task_to_update


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task_to_delete = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).one_or_none()
    if not task_to_delete:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    db.delete(task_to_delete)
    db.commit()
    return {}
