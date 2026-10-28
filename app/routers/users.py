"""
API для работы с сотрудниками
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, User, Position
from app.schemas import UserOut, UserUpdate, MessageResponse
from app.core.access import access
from app.utils.jwt import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


# ===== СВОЙ ПРОФИЛЬ =====

@router.get("/me/profile", response_model=UserOut)
def get_my_profile(current_user=Depends(get_current_user)):
    """Получить свой профиль"""
    return current_user


@router.put("/me/profile", response_model=UserOut)
def update_my_profile(
        user_data: UserUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Обновить свой профиль"""
    if user_data.full_name:
        current_user.full_name = user_data.full_name
    if user_data.specialty is not None:
        current_user.specialty = user_data.specialty

    db.commit()
    db.refresh(current_user)
    return current_user



# специальные едпоинты

@router.get("/by-max-id/{max_id}", response_model=UserOut)
def get_user_by_max_id(
    max_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить пользователя по max_id.
    Используется ботом для проверки регистрации.
    """
    user = db.query(User).filter(User.max_id == max_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

# ===== СПИСОК И РАБОТА С СОТРУДНИКАМИ =====

@router.get("/", response_model=List[UserOut])
def get_users(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Список всех сотрудников (только руководитель)"""
    if not access.can_manage_users(current_user):
        raise HTTPException(status_code=403, detail="Только для руководителя")

    users = db.query(User).filter(User.school_id == current_user.school_id).all()
    return users


@router.get("/{user_id}", response_model=UserOut)
def get_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Информация о сотруднике (только руководитель)"""
    if not access.can_manage_users(current_user):
        raise HTTPException(status_code=403, detail="Только для руководителя")

    user = db.query(User).filter(
        User.id == user_id,
        User.school_id == current_user.school_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
        user_id: int,
        user_data: UserUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Обновить сотрудника (только руководитель)"""
    if not access.can_manage_users(current_user):
        raise HTTPException(status_code=403, detail="Только для руководителя")

    user = db.query(User).filter(
        User.id == user_id,
        User.school_id == current_user.school_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя редактировать себя")

    if user_data.full_name:
        user.full_name = user_data.full_name
    if user_data.specialty is not None:
        user.specialty = user_data.specialty
    if user_data.position:
        user.position = user_data.position

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Удалить сотрудника (только руководитель)"""
    if not access.can_manage_users(current_user):
        raise HTTPException(status_code=403, detail="Только для руководителя")

    user = db.query(User).filter(
        User.id == user_id,
        User.school_id == current_user.school_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя удалить себя")

    user.school_id = None
    user.position = Position.EMPLOYEE
    db.commit()

    return {"ok": True, "message": f"Сотрудник {user.full_name} удалён из организации"}