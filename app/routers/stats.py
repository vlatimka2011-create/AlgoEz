"""Проводник статикии"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, Task, User
from app.schemas import UserStats, OrganizationStats
from app.core.access import access
from app.core.auxiliary import Statistics
from app.utils.jwt import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/me", response_model=UserStats)
def get_my_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Моя статистика"""
    tasks = db.query(Task).filter(Task.assigned_to == current_user.id).all()
    return Statistics.calculate_user_stats(tasks)


@router.get("/organization", response_model=OrganizationStats)
def get_organization_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Статистика организации"""
    if not access.can_view_stats(current_user):
        raise HTTPException(status_code=403, detail="Только для руководителя")

    users = db.query(User).filter(User.school_id == current_user.school_id).all()
    tasks = db.query(Task).filter(Task.school_id == current_user.school_id).all()

    return Statistics.calculate_organization_stats(users, tasks)


@router.get("/user/{user_id}", response_model=UserStats)
def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Статистика конкретного сотрудника"""
    if not access.can_view_stats(current_user):
        raise HTTPException(status_code=403, detail="Только для руководителя")

    user = db.query(User).filter(
        User.id == user_id,
        User.school_id == current_user.school_id
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    tasks = db.query(Task).filter(Task.assigned_to == user_id).all()
    return Statistics.calculate_user_stats(tasks)