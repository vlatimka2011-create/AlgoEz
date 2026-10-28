"""
Меню команд для бота AlgoEz
"""


class BotMenu:
    """Список команд для меню"""

    @staticmethod
    def get_commands() -> list:
        """Получить список команд для меню (максимум 32 элемента)"""
        return [
            {"name": "start", "description": " Начать работу"},
            {"name": "help", "description": " Помощь"},
            {"name": "tasks", "description": " Мои задачи"},
            {"name": "add", "description": " Создать задачу"},
            {"name": "complete", "description": " Выполнить задачу"},
            {"name": "stats", "description": " Моя статистика"},
            {"name": "pochta", "description": " Почтовое бюро"},
        ]