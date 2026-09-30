"""БД"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

from app.core.config import config

# движок
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# модельки

class User(Base):
    """Пользователь"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    max_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id)"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # связи
    school = relationship("School", back_populates="users")

    assigned_tasks = relationship("Task", foreign_keys="[Task.assigned_to]", back_populates="assignee")
    created_tasks = relationship("Task", foreign_keys="[Task.created_by]", back_populates="creator")
