from functools import lru_cache
from typing import Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./compliancematch.db"
    secret_key: str = "change-me-in-production"
    allowed_origins: list[str] = ["*"]

    # Custo por operação (AOEN fase 4 — custo mensurável por cliente)
    cost_match_run: float = 1.0
    cost_project_open: float = 0.5
    cost_per_hire: float = 5.0

    class Config:
        env_file = ".env"


# Configuração por tenant (AOEN fase 3 — config-driven)
TENANT_DEFAULTS: dict[str, Any] = {
    "max_matches_per_project": 10,
    "auto_match": False,
    "require_certification": False,
    "min_freelancer_rating": 0.0,
    "allowed_domains": None,          # None = todos
    "match_weights": {
        "domain_overlap": 0.35,
        "certification_match": 0.25,
        "experience_years": 0.20,
        "rating": 0.15,
        "rate_fit": 0.05,
    },
}

PLAN_LIMITS: dict[str, dict[str, Any]] = {
    "starter": {
        "max_open_projects": 3,
        "max_matches_per_project": 5,
        "monthly_credits": 100,
    },
    "growth": {
        "max_open_projects": 20,
        "max_matches_per_project": 15,
        "monthly_credits": 500,
    },
    "enterprise": {
        "max_open_projects": -1,       # ilimitado
        "max_matches_per_project": 50,
        "monthly_credits": -1,
    },
}


def get_tenant_config(tenant_config_override: dict) -> dict:
    """Mescla defaults com overrides do tenant — núcleo do config-driven."""
    merged = TENANT_DEFAULTS.copy()
    merged.update(tenant_config_override or {})
    if "match_weights" in tenant_config_override:
        weights = TENANT_DEFAULTS["match_weights"].copy()
        weights.update(tenant_config_override["match_weights"])
        merged["match_weights"] = weights
    return merged


@lru_cache
def get_settings() -> Settings:
    return Settings()