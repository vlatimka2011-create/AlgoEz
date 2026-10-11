from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


#  ПОЛЬЗОВАТЕЛИ

class UserBase(BaseModel):
    """Базовая схема пользователя"""
    max_id: int
    full_name: str = Field(..., min_length=2)
    position: str = Field(default="employee")
    specialty: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    school_id: Optional[int] = None


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    full_name: Optional[str] = Field(None, min_length=2)
    specialty: Optional[str] = None
    position: Optional[str] = None


class UserOut(UserBase):
    """Схема для ответа с данными пользователя"""
    id: int
    school_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


#  ОРГАНИЗАЦИИ

class SchoolBase(BaseModel):
    """Базовая схема организации"""
    name: str = Field(..., min_length=2)


class SchoolCreate(SchoolBase):
    """Схема для создания организации"""
    pass


class SchoolOut(SchoolBase):
    """Схема для ответа с данными организации"""
    id: int
    invite_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ЗАДАЧИ

class TaskBase(BaseModel):
    """Базовая схема задачи"""
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=20)
    assigned_to: int
    deadline: datetime
    priority: str = Field(default="normal")


class TaskCreate(TaskBase):
    """Схема для создания задачи"""
    justification: Optional[str] = None  # Обоснование для бюро


class TaskUpdate(BaseModel):
    """Схема для обновления задачи"""
    title: Optional[str] = Field(None, min_length=3)
    description: Optional[str] = Field(None, min_length=20)
    assigned_to: Optional[int] = None
    deadline: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    completion_comment: Optional[str] = None


class TaskOut(BaseModel):
    """Схема для ответа с данными задачи"""
    id: int
    school_id: int
    title: str
    description: str
    assigned_to: int
    created_by: int
    deadline: datetime
    status: str
    priority: str

    # Почтовое бюро
    approval_status: str
    approved_by: Optional[int] = None
    rejection_reason: Optional[str] = None
    justification: Optional[str] = None

    # Временные метки
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    completion_comment: Optional[str] = None

    # Дополнительные поля (заполняются в роутере)
    assignee_name: Optional[str] = None
    creator_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# СТАТИСТИКА

class UserStats(BaseModel):
    """Статистика сотрудника"""
    total_tasks: int
    completed: int
    overdue: int
    completion_rate: float


class EmployeeStats(BaseModel):
    """Статистика по сотруднику (для таблицы руководителя)"""
    id: int
    name: str
    total: int
    completed: int
    rate: float


class OrganizationStats(BaseModel):
    """Статистика организации"""
    total_users: int
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    employees: Optional[List[EmployeeStats]] = None


#  ПОЧТОВОЕ БЮРО

class RejectRequest(BaseModel):
    """Тело запроса на отклонение задачи"""
    reason: str = Field(..., min_length=5, description="Причина отклонения")


#  АУТЕНТИФИКАЦИЯ

class Token(BaseModel):
    """JWT-токен"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные из токена"""
    user_id: Optional[int] = None
    position: Optional[str] = None


class LoginRequest(BaseModel):
    """Запрос на вход"""
    max_id: int


#  ОБЩИЕ

class MessageResponse(BaseModel):
    """Простой ответ с сообщением"""
    ok: bool = True
    message: str