"""
Вспомогательные функции
"""
from sqlalchemy.orm import Session
from app.database import User


def get_user_name(db: Session, user_id: int):
    """Получить имя пользователя по ID"""
    if not user_id:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    return user.full_name if user else None


def enrich_task_with_names(db: Session, task):
    """Добавить имена assignee и creator к задаче"""
    return {
        "assignee_name": get_user_name(db, task.assigned_to),
        "creator_name": get_user_name(db, task.created_by)
    }