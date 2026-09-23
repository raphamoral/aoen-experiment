from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    ADR-001: Configuração externalizada via variáveis de ambiente.
    Decisão reversível: trocar para Vault/AWS SSM sem alterar código de negócio.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Compliance Marketplace"
    debug: bool = False
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    database_url: str = "sqlite+aiosqlite:///./compliance_marketplace.db"

    allowed_origins: List[str] = ["http://localhost:3000"]

    # Fitness threshold: máximo de dependências externas permitidas
    max_external_dependencies: int = 10

    # Fitness threshold: latência máxima aceitável em ms
    max_response_time_ms: int = 500


@lru_cache
def get_settings() -> Settings:
    return Settings()