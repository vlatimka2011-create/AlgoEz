"""
Конфиги AlgoEz
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Конфигурация"""

    # По непосредственно Max боту
    MAX_BOT_TOKEN : str= os.getenv('MAX_BOT_TOKEN', "")
    BOT_KEY : str = os.getenv("BOT_KEY", '')

    # API
    ALGOEZ_API_KEY : str = os.getenv("ALGOEZ_API_KEY", '')
    API_URL: str = os.getenv("API_URL", "http://localhost:8000")
    MINI_APP_URL: str = os.getenv("MINI_APP_URL", "")

    # БД
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./algoez.db")


    # Шифрование
    SECRET_KEY : str = os.getenv("SECRET_KEY", "")
    ALGORITHM : str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES : int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Приложение
    APP_NAME : str = os.getenv("APP_NAME", "AlgoEz")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"


    # Ядро
    ALLOWED_ORIGINS : str = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")

    @classmethod

    def validate(cls) -> None:
        """Проверка настроек"""
        if not cls.SECRET_KEY:
            raise ValueError("Не задан SECRET_KEY!")
        if not cls.MAX_BOT_TOKEN:
            raise ValueError("Не задан MAX_BOT_TOKEN!")

    @classmethod

    def print_summary(cls) -> None:
        """Вывод конфига"""
        print(f"Конфигурация {cls.APP_NAME}")
        print(f"MAX Bot: {'Есть' if cls.MAX_BOT_TOKEN or cls.BOT_KEY else 'Нету'}")
        print(f"БД: {cls.DATABASE_URL}")
        print(f"Debug: {'ВКЛ' if cls.DEBUG else 'ВЫКЛ'}")

config = Config()






























