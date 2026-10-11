from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field

from app.database import get_db, Task, TaskStatus, ApprovalStatus
from app.schemas import TaskOut
from app.core.access import access
from app.utils.jwt import get_current_user

router = APIRouter(prefix="/pochta", tags=["pochta"])


class RejectRequest(BaseModel):
    """Тело запроса на отклонение задачи"""
    reason: str = Field(..., min_length=5, description="Причина отклонения")


@router.get("/pending", response_model=List[TaskOut])
def get_pending_tasks(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Список задач, ожидающих утверждения (только для руководителя)"""
    if not access.is_manager(current_user):
        raise HTTPException(status_code=403, detail="Только для руководителя")

    tasks = db.query(Task).filter(
        Task.school_id == current_user.school_id,
        Task.approval_status == ApprovalStatus.PENDING
    ).all()

    return tasks


@router.post("/{task_id}/approve")
def approve_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Утвердить задачу"""
    if not access.can_approve_task(current_user):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task.approval_status = ApprovalStatus.APPROVED
    task.approved_by = current_user.id
    task.status = TaskStatus.NEW
    db.commit()

    return {"ok": True, "message": "Задача утверждена"}


@router.post("/{task_id}/reject")
def reject_task(
    task_id: int,
    rejection: RejectRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Отклонить задачу с указанием причины"""
    if not access.can_approve_task(current_user):
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task.approval_status = ApprovalStatus.REJECTED
    task.rejection_reason = rejection.reason
    db.commit()

    return {
        "ok": True,
        "message": "Задача отклонена",
        "reason": rejection.reason
    }