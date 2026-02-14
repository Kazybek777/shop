import json
from pathlib import Path
from typing import Annotated, List

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode


class Settings(BaseSettings):
    backend_dir: str = str(Path(__file__).resolve().parent.parent)

    app_name: str = "TashTemir"
    debug: bool = True
    database_url: str = "sqlite:///./shop.db"

    cors_origins: Annotated[List[str], NoDecode] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    static_dir: str = str(Path(__file__).resolve().parent.parent / "static")
    images_dir: str = str(Path(__file__).resolve().parent.parent / "static" / "images")

    secret_key: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    google_client_id: str = ""
    google_client_secret: str = ""
    admin_emails: Annotated[List[str], NoDecode] = []

    @staticmethod
    def _parse_string_list(value):
        if value in (None, "", []):
            return []

        if isinstance(value, list):
            return [str(item).strip().lower() for item in value if str(item).strip()]

        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []

            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    parsed = raw.strip("[]").split(",")
            else:
                parsed = raw.split(",")

            normalized = []
            for item in parsed:
                value_item = str(item).strip().strip('"').strip("'").lower()
                if value_item:
                    normalized.append(value_item)
            return normalized

        raise ValueError("value must be a list or comma-separated string")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        return cls._parse_string_list(value)

    @field_validator("admin_emails", mode="before")
    @classmethod
    def parse_admin_emails(cls, value):
        return cls._parse_string_list(value)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
