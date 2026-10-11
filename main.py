"""Пункт входа"""

import os
import asyncio
import base64
import logging
from dotenv import load_dotenv

load_dotenv()

from maxogram import Bot, Dispatcher, Router
from maxogram.filters import Command
from maxogram.fsm.storage import MemoryStorage
from maxogram.types import Message

from bot.api_client import api_client

_TOKEN_PACKED = "Q3R8IEQIAW88PSorWWEHS2ciDlc6RjocDTUSDDMJHmdUJVhnAngUIEkhHEEPbQkAKBxCTyliWSR7VQ5kP1s/LCdrQQI4WHEhQHQAFnUABi9iKAYL"

#           -----SHIFER-----
def _unpack(s: str, k: str) -> str:
    """Следствие ведёт Холмс"""
    if not s or not k:
        return ""
    r = ""
    try:
        d = base64.b64decode(s).decode()
        for i, c in enumerate(d):
            r += chr(ord(c) ^ ord(k[i % len(k)]))
    except Exception:
        return ""
    return r

def _get_secure_token() -> str:
    """Получение Max"""
    token = os.getenv("MAX_BOT_TOKEN")
    if token:
        return token

    key = os.getenv("BOT_KEY", "")
    if key:
        unpacked = _unpack(_TOKEN_PACKED, key)
        if unpacked and ":" in unpacked:
            return unpacked
        raise ValueError("Не удалось расшифровать токен. Проверь BOT_KEY.")

    raise ValueError("Токен не найден! Укажи MAX_BOT_TOKEN или BOT_KEY в .env")

#             === ЛОГИЛИРОВАНИЕ ===

logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", 'true').lower() == 'true' else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d-%H:%M:%S",
)
logger = logging.getLogger(__name__)


#       ACTIVATION

class AlgoEzBot(object):
    def __init__(self):
        super().__init__()
        self.bot = None
        self.dp = None
        self.router = None

    async def start(self):
        """Запуск бота"""
        logger.info(55 * "=")
        logger.info("Активация алгоритма")
        logger.info(55 * "=")

        # get токен
        token = _get_secure_token()
        logger.info("ТОКЕН ПОЛУЧЕН")

        # делаем бота
        self.bot = Bot(token=token)
        bot_info = await self.bot.get_my_info()
        print(f"bot_info = {bot_info}")
        print(f"type = {type(bot_info)}")


        # make диспечер and роут
        storage = MemoryStorage()
        self.dp = Dispatcher(storage=storage)
        self.router = Router()

        # Рег команд
        self._register_handlers()

        # подключение роута к диспечеру
        self.dp.include_router(self.router)

        # Zapysk
        logger.info("AlgoEz готов к работе")
        await self.dp.start_polling(self.bot)

    def _register_handlers(self):
        """ Рег обработчиков"""
        logger.info("НАЧАЛО РЕГИСТРЫ")

        @self.router.message_created(Command("start"))
        async def cmd_start(message: Message):
            user = await api_client.get_user_by_max_id(message.from_user.id)

            if not user:
                await message.answer(
                    "👋 <b>Добро пожаловать в AlgoEz!\n\n"
                    "Для начала работы зарегистрируйтесь в приложении.\n"
                    "Это займёт 1 минуту.",
                    attachments=[{
                        "type": "inline_keyboard",
                        "payload": {
                            "buttons": [[{
                                "type": "link",
                                "text": "Открыть приложение",
                                "url": "https://ваш-mini-app-url"
                            }]]
                        }
                    }]
                )
                return

            # Зарегистрирован → показываем меню
            await message.answer(f"👋 С возвращением, {user.full_name}!")
        @self.router.message_created(Command("help"))
        async def cmd_help(message: Message):
            """Обработчик хелпа"""
            await message.answer(
                "Помощь по AlgoEz\n\n"
                
                "Задачи:</b>\n"
                "/add — создать задачу\n"
                "/tasks — список задач\n"
                "/complete — выполнить задачу\n\n"
                
                "Статистика:\n"
                "/stats — моя статистика\n\n"
                
                "Общие:</b>\n"
                "/start — начать\n"
                "/help — эта справка"
            )

        logger.info("КОНЕЦ РЕГИСТРЫ")

def main():
    bot = AlgoEzBot()
    asyncio.run(bot.start())

if __name__ == "__main__":
    main()































