from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "NutriAI"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Banco de dados
    # ADR-001: SQLite para MVP. Trocar DATABASE_URL para migrar sem tocar repositories.
    DATABASE_URL: str = "sqlite+aiosqlite:///./nutriai.db"

    # AI Provider — ADR-002: abstração reversível via Protocol
    AI_PROVIDER: str = "mock"  # "mock" | "openai"
    AI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"

    # Thresholds consumidos pelas fitness functions — fonte única de verdade
    MAX_RESPONSE_TIME_MS: int = 500
    MAX_MODULE_COUPLING: int = 8  # dependencies.py é wiring layer; threshold generoso


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()