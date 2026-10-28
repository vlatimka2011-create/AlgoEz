"""Пункт входа для бота"""

import os
import asyncio
import base64
import logging
from dotenv import load_dotenv

load_dotenv()

from maxogram import Bot, Dispatcher, Router
from maxogram.fsm.storage import MemoryStorage


from app.core.config import config
from bot.menu import BotMenu
from bot.api_client import api_client
from bot.api_client import APIClient

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
    except (ValueError, UnicodeDecodeError, IndexError):
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

        await APIClient.set_bot_commands(BotMenu.get_commands(), token)
        logger.info("✅ Меню команд настроено")

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
        """Регистрация всех обработчиков"""
        logger.info("Старт рега")

        from bot.handlers import register_all_handlers
        register_all_handlers(self.router, config.MINI_APP_URL)

        logger.info("Конец рега")

def main():
    bot = AlgoEzBot()
    asyncio.run(bot.start())

if __name__ == "__main__":
    main()































