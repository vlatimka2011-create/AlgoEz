from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db, User, School, Position
from app.schemas import (
    UserCreate, UserOut, UserUpdate,
    Token, LoginRequest, MessageResponse
)
from app.core.auxiliary import InviteSystem
from app.utils.jwt import create_access_token, get_current_user
from app.core.config import config

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(
        login_data: LoginRequest,
        db: Session = Depends(get_db)
):
    """
    Вход по max_id (автоматически из MAX Bridge).
    """
    user = db.query(User).filter(User.max_id == login_data.max_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден. Зарегистрируйтесь."
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "position": user.position},
        expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut)
def register(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя (через Mini App).
    """
    existing = db.query(User).filter(User.max_id == user_data.max_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже зарегистрирован")

    # Создаём пользователя
    new_user = User(
        max_id=user_data.max_id,
        full_name=user_data.full_name,
        position=user_data.position or Position.EMPLOYEE,
        specialty=user_data.specialty,
        school_id=user_data.school_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(
        user_data: UserUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Обновить свой профиль.
    """
    if user_data.full_name:
        current_user.full_name = user_data.full_name
    if user_data.specialty is not None:
        current_user.specialty = user_data.specialty

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/create-school", response_model=UserOut)
def create_school_for_user(
        school_name: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Создать организацию для текущего пользователя.
    Пользователь становится руководителем.
    """
    if current_user.school_id:
        raise HTTPException(status_code=400, detail="Вы уже в организации")

    invite_code = InviteSystem.generate_invite_code(school_name)

    school = School(
        name=school_name,
        invite_code=invite_code
    )
    db.add(school)
    db.commit()
    db.refresh(school)

    current_user.school_id = school.id
    current_user.position = Position.MANAGER
    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/join-school", response_model=UserOut)
def join_school(
        invite_code: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Присоединиться к организации по invite-коду.
    """
    if current_user.school_id:
        raise HTTPException(status_code=400, detail="Вы уже в организации")

    if not InviteSystem.validate_invite_code_format(invite_code):
        raise HTTPException(status_code=400, detail="Неверный формат кода")

    school = db.query(School).filter(School.invite_code == invite_code).first()
    if not school:
        raise HTTPException(status_code=404, detail="Организация не найдена")

    current_user.school_id = school.id
    current_user.position = Position.EMPLOYEE
    db.commit()
    db.refresh(current_user)

    return current_user