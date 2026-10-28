"""
Обработчик команды /help
"""
from maxogram.filters import Command
from maxogram.types import Message


def register_help_handlers(router):
    """Регистрация обработчиков /help"""

    @router.message_created(Command("help"))
    async def cmd_help(message: Message):
        """Обработчик /help"""
        await message.answer(
            "Помощь по чат-боту AlgoEz\n\n"
            "Задачи:\n"
            "/tasks — список моих задач\n"
            "/add — создать задачу\n"
            "/complete — выполнить задачу\n\n"
            "Статистика:\n"
            "/stats — моя статистика\n\n"
            "Задачи, созданные сотрудником сотруднику, но требующие утверждения от руководителя:\n"
            "/pochta — заявки задач на утверждение (руководителю)\n\n"
            "Общие:\n"
            "/start — начать\n"
        )