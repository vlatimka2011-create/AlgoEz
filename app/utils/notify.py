import aiohttp
import logging
from app.core.config import config

logger = logging.getLogger(__name__)


async def notify_user(max_id: int, text: str) -> bool:
    """
    Отправить уведомление пользователю в MAX из веба
    """
    url = "https://platform-api2.max.ru/messages"
    headers = {
        "Authorization": config.MAX_BOT_TOKEN,
        "Content-Type": "application/json"
    }
    data = {
        "user_id": max_id,
        "text": text
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    logger.info(f"Уведомление отправлено {max_id}")
                    return True
                else:
                    error = await response.text()
                    logger.error(f"Ошибка отправки: {response.status} - {error}")
                    return False
    except Exception as e:
        logger.error(f"Исключение: {e}")
        return False