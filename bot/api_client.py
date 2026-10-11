"""
Связной бота с API
"""
import aiohttp
import logging
from typing import Optional, List

from app.core.config import config

logger = logging.getLogger(__name__)


class APIClient:
    """Клиент для работы с API AlgoEz"""

    def __init__(self):
        self.base_url = config.API_URL  # например, http://localhost:8000
        self.headers = {"X-API-Key": config.ALGOEZ_API_KEY}

    async def _request(self, method: str, endpoint: str, data: dict = None) -> Optional[dict]:
        """Базовый запрос к API"""
        url = f"{self.base_url}{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, json=data, headers=self.headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"API error {response.status}: {await response.text()}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка запроса к API: {e}")
            return None

    async def get_user_by_max_id(self, max_id: int) -> Optional[dict]:
        """Получить пользователя по max_id"""
        return await self._request("GET", f"/api/users/by-max-id/{max_id}")

    async def get_user_tasks(self, user_id: int) -> Optional[List[dict]]:
        """Получить задачи пользователя"""
        return await self._request("GET", f"/api/tasks/user/{user_id}")

    async def create_task(self, task_data: dict) -> Optional[dict]:
        """Создать задачу"""
        return await self._request("POST", "/api/tasks", task_data)


api_client = APIClient()