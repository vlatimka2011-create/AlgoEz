from maxogram.filters import Command
from maxogram.types import Message

from bot.api_client import api_client


def register_start_handlers(router, mini_app_url: str):
    """Регистрация обработчиков /start"""

    @router.message_created(Command("start"))
    async def cmd_start(message: Message):
        """Обработчик /start"""
        # Проверяем регистрацию через API
        user = await api_client.get_user_by_max_id(message.sender.user_id)

        if not user:
            # Не зарегистрирован → отправляем в Mini App
            await message.answer(
                "👋 <b>Добро пожаловать в AlgoEz!</b>\n\n"
                "Для начала работы зарегистрируйтесь в приложении.\n"
                "Это займёт 1 минуту.",
                attachments=[{
                    "type": "inline_keyboard",
                    "payload": {
                        "buttons": [[{
                            "type": "link",
                            "text": "📝 Открыть приложение",
                            "url": mini_app_url
                        }]]
                    }
                }]
            )
            return

        # Зарегистрирован → приветствие
        await message.answer(
            f"С возвращением, {user['full_name']}!</b>\n\n"
            f"Используйте /help для списка команд."
        )