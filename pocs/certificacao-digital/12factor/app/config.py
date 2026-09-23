from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Factor III: toda configuração vem do ambiente, nunca hardcoded
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    database_url: str
    secret_key: str
    app_name: str = "CertificaDigital"
    environment: str = "production"
    port: int = 8000
    allowed_origins: str = "*"
    certificate_issuer: str = "Plataforma CertificaDigital"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()