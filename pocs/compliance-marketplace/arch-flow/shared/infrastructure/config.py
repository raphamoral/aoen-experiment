from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ComplianceHub Marketplace"
    app_version: str = "1.0.0"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./compliancehub.db"
    secret_key: str = "change-me-in-production-use-env-var"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Integrações externas (COMMODITY — terceirizar em produção)
    stripe_api_key: str = ""
    oauth_provider_url: str = ""       # Auth0 / Keycloak
    docusign_api_key: str = ""         # Assinatura digital

    class Config:
        env_file = ".env"


settings = Settings()