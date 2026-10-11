# Вспомогалки
import string
import secrets
from datetime import datetime, timezone, timedelta
from typing import List, Dict


class TaskValidator:
    """Валидация"""

    @staticmethod
    def validate_task_creation(title: str, description: str) -> bool:
        """Проверка при создании задачи"""
        if len(title.strip()) < 3:
            raise ValueError("Название задачи должно быть ≥ 3 символов")
        if len(description.strip()) < 20:
            raise ValueError("Описание задачи должно быть ≥ 20 символов")
        return True

    @staticmethod
    def validate_completion_comment(comment: str) -> bool:
        """Проверка комментария при выполнении"""
        if comment and len(comment.strip()) < 10:
            raise ValueError("Комментарий должен быть ≥ 10 символов")
        return True

    @staticmethod
    def validate_deadline(deadline: datetime) -> bool:
        """Проверка, что дедлайн в будущем"""
        now = datetime.now(timezone.utc)
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if deadline <= now:
            raise ValueError("Дедлайн должен быть в будущем")
        return True


class PriorityCalculator:
    """Расчёт приоритетов задач по времени"""

    @staticmethod
    def is_urgent(deadline: datetime, urgent_hours: int = 24) -> bool:
        """Определение срочности задачи"""
        now = datetime.now(timezone.utc)
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        time_left = deadline - now
        return timedelta(seconds=0) < time_left < timedelta(hours=urgent_hours)

    @staticmethod
    def get_priority_level(deadline: datetime) -> str:
        """Получить уровень приоритета на основе дедлайна"""
        now = datetime.now(timezone.utc)
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        time_left = deadline - now

        if time_left < timedelta(hours=1):
            return "critical"
        elif time_left < timedelta(hours=24):
            return "urgent"
        elif time_left < timedelta(days=3):
            return "high"
        else:
            return "normal"


class InviteSystem:
    """Логика работы с приглашением в оргу"""

    @staticmethod
    def validate_invite_code_format(code: str) -> bool:
        """Проверка формата invite-кода: XXX-XXXX"""
        if not code or '-' not in code:
            return False
        parts = code.split('-')
        if len(parts) != 2:
            return False
        prefix, suffix = parts
        return (len(prefix) == 3 and prefix.isalpha() and
                len(suffix) == 4 and suffix.isalnum())

    @staticmethod
    def generate_invite_code(school_name: str) -> str:
        """Генерация уникального invite-кода"""
        prefix = ''.join(c for c in school_name[:3].upper() if c.isalpha())
        if len(prefix) < 3:
            prefix = "SCH"

        random_part = ''.join(
            secrets.choice(string.ascii_uppercase + string.digits)
            for _ in range(4)
        )
        return f"{prefix}-{random_part}"

    @staticmethod
    def is_invite_expired(created_at: datetime, expire_days: int = 7) -> bool:
        """Проверить, истёк ли срок действия кода"""
        now = datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return now > created_at + timedelta(days=expire_days)


class Statistics:
    """Статика"""

    @staticmethod
    def calculate_user_stats(tasks: List) -> Dict:
        """Статистика сотрудника"""
        if not tasks:
            return {
                "total_tasks": 0,
                "completed": 0,
                "overdue": 0,
                "completion_rate": 0
            }

        now = datetime.now(timezone.utc)
        total = len(tasks)
        completed = len([t for t in tasks if t.status == "done"])
        overdue = len([
            t for t in tasks
            if t.status != "done" and _to_aware(t.deadline) < now
        ])

        return {
            "total_tasks": total,
            "completed": completed,
            "overdue": overdue,
            "completion_rate": round(completed / total * 100, 1) if total > 0 else 0
        }

    @staticmethod
    def calculate_organization_stats(users: List, tasks: List) -> Dict:
        """Статистика организации"""
        total_users = len(users)
        total_tasks = len(tasks)

        if not tasks:
            return {
                "total_users": total_users,
                "total_tasks": 0,
                "completed_tasks": 0,
                "completion_rate": 0
            }

        completed = len([t for t in tasks if t.status == "done"])

        return {
            "total_users": total_users,
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "completion_rate": round(completed / total_tasks * 100, 1)
        }


class Pagination:
    """Логика пагинации"""

    PAGE_SIZE = 5

    @staticmethod
    def get_page_data(items: List, page: int = 1, page_size: int = None) -> Dict:
        """Разбить список на страницы"""
        if page_size is None:
            page_size = Pagination.PAGE_SIZE

        if not items:
            return {
                "items": [],
                "page": 1,
                "pages": 0,
                "total": 0,
                "has_next": False,
                "has_prev": False
            }

        total = len(items)
        pages = max(1, (total + page_size - 1) // page_size)
        page = max(1, min(page, pages))

        start = (page - 1) * page_size
        end = start + page_size

        return {
            "items": items[start:end],
            "page": page,
            "pages": pages,
            "total": total,
            "has_next": page < pages,
            "has_prev": page > 1
        }


class RegistrationFlow:
    """Процесс регистрации пользователей"""

    @staticmethod
    def generate_welcome_message(position: str, school_name: str) -> str:
        """Приветственное сообщение"""
        if position == "manager":
            return f"Добро пожаловать, руководитель! Вы создали организацию '{school_name}'."
        else:
            return f"Добро пожаловать, сотрудник! Вы присоединились к '{school_name}'."

    @staticmethod
    def get_position_description(position: str) -> str:
        """Описание должности для пользователя"""
        descriptions = {
            "manager": "Полный доступ к управлению организацией",
            "employee": "Выполнение задач и просмотр статистики"
        }
        return descriptions.get(position, "Должность не определена")


def _to_aware(dt: datetime) -> datetime:
    """Приводит datetime к timezone-aware (UTC)"""
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


__all__ = [
    'TaskValidator',
    'PriorityCalculator',
    'InviteSystem',
    'Statistics',
    'Pagination',
    'RegistrationFlow'
]
