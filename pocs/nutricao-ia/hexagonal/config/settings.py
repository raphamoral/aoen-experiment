from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application
    app_name: str = "NutriAI"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./nutriai.db"

    # Anthropic
    anthropic_api_key: str
    anthropic_model: str = "claude-opus-4-6"

    # SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_sender_email: str = "noreply@nutriai.app"
    smtp_use_tls: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()