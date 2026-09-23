from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./compliance_marketplace.db"
    app_title: str = "Compliance Freelancer Marketplace"
    app_version: str = "1.0.0"
    debug: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()