"""
Подключение к базе данных AlgoEz
"""
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Boolean, 
    ForeignKey, Text, JSON
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime, timezone

from app.core.config import config

# движок
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ДОЛЖНОСТИ

class Position:
    """Должности (упрощённо)"""
    MANAGER = "manager"      # Руководитель (директор, завуч)
    EMPLOYEE = "employee"    # Сотрудник (все остальные)


POSITION_NAMES = {
    Position.MANAGER: "Руководитель",
    Position.EMPLOYEE: "Сотрудник",
}


# СТАТУСЫ

class TaskStatus:
    """Статусы задач"""
    PENDING_APPROVAL = "pending_approval"  # В почтовом бюро
    NEW = "new"                             # Назначена исполнителю
    IN_PROGRESS = "in_progress"             # В работе
    DONE = "done"                           # Выполнена
    DECLINED = "declined"                   # Отклонена исполнителем
    REJECTED = "rejected"                   # Отклонена руководителем
    UNASSIGNED = "unassigned"               # Без исполнителя


class TaskPriority:
    """Приоритеты"""
    NORMAL = "normal"
    IMPORTANT = "important"
    URGENT = "urgent"


class ApprovalStatus:
    """Статусы утверждения"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# Модельки

class User(Base):
    """Пользователь AlgoEz"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    max_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String, nullable=False)

    # Должность (административная)
    position = Column(String, nullable=False, default=Position.EMPLOYEE)

    # Специальность (профессиональная) — сотрудник ставит сам
    specialty = Column(String, nullable=True)

    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Связи
    school = relationship("School", back_populates="users")
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    created_tasks = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    approved_tasks = relationship("Task", foreign_keys="Task.approved_by", back_populates="approver")


class School(Base):
    """Организация (школа)"""
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    invite_code = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Связи
    users = relationship("User", back_populates="school")
    tasks = relationship("Task", back_populates="school")


class Task(Base):
    """Задача"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    deadline = Column(DateTime, nullable=False)
    status = Column(String, default=TaskStatus.NEW)
    priority = Column(String, default=TaskPriority.NORMAL)

    # ===== ПОЧТОВОЕ БЮРО =====
    approval_status = Column(String, default=ApprovalStatus.APPROVED)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    justification = Column(Text, nullable=True)

    # ===== ВРЕМЕННЫЕ МЕТКИ =====
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    completed_at = Column(DateTime, nullable=True)
    completion_comment = Column(Text, nullable=True)

    # Связи
    school = relationship("School", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tasks") # type: ignore
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tasks") # type: ignore
    approver = relationship("User", foreign_keys=[approved_by], back_populates="approved_tasks") # type: ignore


# def-ки

def get_db():
    """Генератор сессий для FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Создать все таблицы"""
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы")
