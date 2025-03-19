from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    USER: str
    PASSWORD: str
    ADDRESS: str
    PORT: int
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    class Config:
        env_file = Path(__file__).parent.parent / ".env"  # Указывает на файл .env
        env_file_encoding = "utf-8"


# Создание экземпляра настроек
settings = Settings()
