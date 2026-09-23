from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./certchain.db"
    secret_key: str = "dev-secret-key-change-in-production"
    environment: str = "development"
    base_url: str = "http://localhost:8000"
    api_v1_prefix: str = "/api/v1"

    # ISOLAMENTO: limites de custo mensuráveis por tenant
    default_max_certificates_per_month: int = 100
    default_max_courses: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()


# CONFIG-DRIVEN: cada tenant herda defaults e sobrescreve o que precisar
class TenantConfig:
    """
    Parâmetros configuráveis por cliente — o fluxo de certificação permanece
    idêntico no código; apenas estes valores mudam entre tenants.
    """

    DEFAULTS: dict[str, Any] = {
        "certificate_template": "default",
        "primary_color": "#1a3a5c",
        "logo_url": None,
        "validity_years": 2,
        "max_certificates_per_month": 100,
        "max_courses": 10,
        "webhook_url": None,
        "public_verification_enabled": True,
        "issuer_name": "CertChain",
        "issuer_country": "BR",
    }

    def __init__(self, raw: dict[str, Any]) -> None:
        self._data = {**self.DEFAULTS, **raw}

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    @classmethod
    def from_json(cls, json_str: str | None) -> "TenantConfig":
        raw = json.loads(json_str) if json_str else {}
        return cls(raw)