"""
Точка входа для API (FastAPI)
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import  auth_router, tasks_router, pochta_router, stats_router, users_router
from app.core.config import config



@asynccontextmanager
async def lifespan(_: FastAPI):
    """Действия при запуске и завершении приложения"""
    # Запуск
    init_db()
    config.print_summary()
    yield
    # Завершение (если нужно)


app = FastAPI(
    title=config.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(pochta_router)
app.include_router(stats_router)
app.include_router(users_router)
