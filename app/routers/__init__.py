from .auth import router as auth_router
from .task_routes import router as tasks_router
from .pochta import router as pochta_router
from .stats import router as stats_router
from .users import router as users_router

__all__ = ['auth_router', 'tasks_router', 'pochta_router', 'stats_router', 'users_router']