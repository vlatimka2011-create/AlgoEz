from .start import register_start_handlers
from .help import register_help_handlers
from .task_handlers import register_task_handlers


def register_all_handlers(router, mini_app_url: str):
    """Регистрация всех обработчиков бота"""
    register_start_handlers(router, mini_app_url)
    register_help_handlers(router)
    register_task_handlers(router)