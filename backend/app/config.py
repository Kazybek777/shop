# app/config.py (или core/config.py, как тебе удобнее)

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "Shop"
    debug: bool = True

    # Рекомендуемый формат для sqlite (относительно текущей папки)
    database_url: str = "sqlite:///./shop.db"

    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    static_dir: str = "static"
    images_dir: str = "static/images"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()