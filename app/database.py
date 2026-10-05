"""БД"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime, timezone

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

class School(Base):
    """Орга"""
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String, nullable=False)
    invite_code = Column(String, unique=True, index=True )
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    users = relationship("User", back_populates="school")
    tasks = relationship("Task", back_populates="school")

class Task(Base):
    """Zadachky"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index = True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(String, default="new")
    priority = Column(Integer, default="normal")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    completion_comment = Column(Text, nullable=True)

    school = relationship("School", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tasks") # type: ignore
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tasks") # type: ignore

    # Функции

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
print("Tablicy ready!")
