from app.database import Position, POSITION_NAMES


class AccessControl:
    """НКВД)))"""

    @staticmethod
    def is_manager(user) -> bool:
        """Является ли пользователь руководителем?"""
        return user and user.position == Position.MANAGER

    @staticmethod
    def is_employee(user) -> bool:
        """Является ли пользователь сотрудником?"""
        return user and user.position == Position.EMPLOYEE

    @staticmethod
    def can_create_task(user) -> bool:
        """Может ли создавать задачи? (могут все)"""
        return user is not None

    @staticmethod
    def can_approve_task(user) -> bool:
        """Может ли утверждать задачи в бюро? (только руководитель)"""
        return AccessControl.is_manager(user)

    @staticmethod
    def can_view_all_tasks(user) -> bool:
        """Может ли видеть все задачи? (только руководитель)"""
        return AccessControl.is_manager(user)

    @staticmethod
    def can_manage_users(user) -> bool:
        """Может ли управлять пользователями? (только руководитель)"""
        return AccessControl.is_manager(user)

    @staticmethod
    def can_view_stats(user) -> bool:
        """Может ли видеть статистику организации? (только руководитель)"""
        return AccessControl.is_manager(user)

    @staticmethod
    def can_invite(user) -> bool:
        """Может ли генерировать invite-коды? (только руководитель)"""
        return AccessControl.is_manager(user)

    @staticmethod
    def can_delete_task(user) -> bool:
        """Может ли удалять задачи? (только руководитель)"""
        return AccessControl.is_manager(user)

    @staticmethod
    def can_edit_task(user) -> bool:
        """Может ли редактировать задачи? (только руководитель)"""
        return AccessControl.is_manager(user)

    @staticmethod
    def can_complete_task(user) -> bool:
        """Может ли выполнять задачи? (могут все)"""
        return user is not None

    # Почтовое бюро

    @staticmethod
    def needs_approval(creator, assignee) -> bool:
        """
        Нужно ли утверждение руководителя?
        """
        if not creator or not assignee:
            return True

        # Руководитель может утверждать сам
        if AccessControl.is_manager(creator):
            return False

        # Назначает сам себе — не нужно
        if creator.id == assignee.id:
            return False

        # Иначе — нужно утверждение
        return True

    @staticmethod
    def get_position_name(position: str) -> str:
        """Получить читаемое название должности"""
        return POSITION_NAMES.get(position, "Неизвестно")


access = AccessControl()

__all__ = ['access', 'AccessControl']