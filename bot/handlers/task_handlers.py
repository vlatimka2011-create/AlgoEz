"""
Обработчики команд для работы с задачами
"""
from maxogram.filters import Command
from maxogram.types import Message

from bot.api_client import api_client


def register_task_handlers(router):
    """Регистрация обработчиков задач"""

    @router.message_created(Command("tasks"))
    async def cmd_tasks(message: Message):
        """Обработчик /tasks — список задач"""
        user = await api_client.get_user_by_max_id(message.sender.user_id)
        if not user:
            await message.answer(
                "Вы не зарегистрированы.\n"
                "Откройте приложение и зарегистрируйтесь."
            )
            return

        # Получаем задачи
        tasks = await api_client.get_user_tasks(user['id'])

        if not tasks:
            await message.answer("У вас нет задач.")
            return

        # Формируем текст
        text = "Ваши задачи:\n\n"
        for task in tasks[:10]:  # показываем первые 10
            status_icon = {
                "new": "🆕",
                "in_progress": "🔄",
                "done": "✅",
                "declined": "❌",
                "pending_approval": "⏳"
            }.get(task['status'], "📝")

            text += f"{status_icon} <b>{task['title']}</b>\n"
            text += f"   🆔 {task['id']}\n"
            text += f"   ⏰ {task['deadline'][:10]}\n\n"

        if len(tasks) > 10:
            text += f"... и ещё {len(tasks) - 10} задач\n"

        text += "\n💡 Используйте /complete ID чтобы выполнить задачу"

        await message.answer(text)

    @router.message_created(Command("add"))
    async def cmd_add(message: Message):
        """Обработчик /add — создать задачу"""
        await message.answer(
            "Создание задачи\n\n"
            "Для создания задачи откройте приложение:\n"
            "Нажмите на кнопку «Открыть приложение» в /start\n\n"
            "💡 В приложении удобнее указывать все параметры задачи."
        )

    @router.message_created(Command("complete"))
    async def cmd_complete(message: Message):
        """Обработчик /complete — выполнить задачу"""
        args = message.text.split()
        if len(args) < 2:
            await message.answer(
                "Укажите ID задачи:\n"
                "/complete 42"
            )
            return

        try:
            task_id = int(args[1])
        except ValueError:
            await message.answer("ID должен быть числом")
            return

        # Получаем пользователя
        user = await api_client.get_user_by_max_id(message.sender.user_id)
        if not user:
            await message.answer("Вы не зарегистрированы.")
            return

        # Отправляем запрос на выполнение
        result = await api_client.complete_task(task_id)

        if result and result.get("ok"):
            await message.answer(f"Задача #{task_id} выполнена!")
        else:
            await message.answer(
                f"Не удалось выполнить задачу #{task_id}\n"
                f"Возможно, она назначена не вам."
            )
