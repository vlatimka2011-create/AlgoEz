"""
API для работы с задачами
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.database import get_db, Task, User, TaskStatus, ApprovalStatus
from app.schemas import TaskCreate, TaskUpdate, TaskOut
from app.core.access import access
from app.core.auxiliary import TaskValidator
from app.utils.jwt import get_current_user
from app.utils.helpers import enrich_task_with_names
from app.utils.notify import notify_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

logger = logging.getLogger(__name__)


@router.get("/", response_model=List[TaskOut])
def get_tasks(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        status: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Получить список задач (с фильтрами)"""
    query = db.query(Task).filter(Task.school_id == current_user.school_id)

    if not access.can_view_all_tasks(current_user):
        query = query.filter(Task.assigned_to == current_user.id)

    # Фильтр по статусу
    if status:
        query = query.filter(Task.status == status)

    # Пагинация
    tasks = query.order_by(Task.deadline).offset(skip).limit(limit).all()

    # Обогащаем именами
    result = []
    for task in tasks:
        task_out = TaskOut.model_validate(task)
        enriched = enrich_task_with_names(db, task)
        task_out.assignee_name = enriched.get("assignee_name")
        task_out.creator_name = enriched.get("creator_name")
        result.append(task_out)

    return result


@router.post("/", response_model=TaskOut)
async def create_task(
        task_data: TaskCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Создать новую задачу"""
    if not access.can_create_task(current_user):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    # Валидация
    TaskValidator.validate_task_creation(task_data.title, task_data.description)
    TaskValidator.validate_deadline(task_data.deadline)

    # Проверяем, что исполнитель существует
    assignee = db.query(User).filter(User.id == task_data.assigned_to).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Исполнитель не найден")

    needs_approval = access.needs_approval(current_user, assignee)

    # Создаём задачу
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        assigned_to=task_data.assigned_to,
        created_by=current_user.id,
        deadline=task_data.deadline,
        priority=task_data.priority,
        school_id=current_user.school_id,
        justification=task_data.justification if needs_approval else None,
        approval_status=ApprovalStatus.PENDING if needs_approval else ApprovalStatus.APPROVED,
        status=TaskStatus.PENDING_APPROVAL if needs_approval else TaskStatus.NEW
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    if not needs_approval:
        assignee = db.query(User).filter(User.id == task_data.assigned_to).first()
        if assignee:
            try:
                await notify_user(
                    assignee.max_id, #type: ignore
                    f"📋 Новая задача: {task_data.title}\n"
                    f"Дедлайн: {task_data.deadline.strftime('%d.%m.%Y')}"
                )
            except Exception as e:
                logger.warning(f"Не удалось уведомить: {e}")


    return new_task


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Получить детали задачи по ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # чек доступ
    if not access.can_view_all_tasks(current_user):
        if task.assigned_to != current_user.id and task.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")

    task_out = TaskOut.model_validate(task)
    enriched = enrich_task_with_names(db, task)
    task_out.assignee_name = enriched.get("assignee_name")
    task_out.creator_name = enriched.get("creator_name")

    return task_out


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
        task_id: int,
        task_data: TaskUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Обновить задачу"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # Проверяем права
    if not access.can_edit_task(current_user):
        if task.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="Нет прав на редактирование")

    # Обновляем поля
    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Удалить задачу"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # Проверяем права
    if not access.can_delete_task(current_user):
        if task.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="Нет прав на удаление")

    db.delete(task)
    db.commit()
    return {"ok": True, "message": "Задача удалена"}


@router.post("/{task_id}/complete")
def complete_task(
        task_id: int,
        comment: str = None,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Отметить задачу как выполненную"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # Проверяем, что задача назначена текущему пользователю
    if task.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Эта задача назначена не вам")

    # Меняем статус
    task.status = TaskStatus.DONE
    task.completed_at = datetime.now(timezone.utc)
    task.completion_comment = comment
    db.commit()

    return {"ok": True, "message": "Задача выполнена"}