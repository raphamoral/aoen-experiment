from functools import lru_cache
from typing import Dict, List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class BiomarkerRange(BaseModel):
    min_normal: float
    max_normal: float
    unit: str
    critical_low: Optional[float] = None
    critical_high: Optional[float] = None


class TenantConfig(BaseModel):
    """
    FASE 3 — CONFIG-DRIVEN: todo comportamento variável por cliente vive aqui.
    O fluxo (análise → plano → recomendação) é fixo no código;
    os parâmetros são configuráveis sem deploy.
    """

    name: str
    ai_model: str = "claude-sonnet-4-6"
    max_daily_analyses: int = 100
    enabled_biomarkers: List[str] = []
    custom_reference_ranges: Dict[str, BiomarkerRange] = {}
    report_language: str = "pt-BR"
    include_supplement_recommendations: bool = True
    include_lifestyle_recommendations: bool = True


# ── Configurações por tenant ──────────────────────────────────────────────────
TENANT_CONFIGS: Dict[str, TenantConfig] = {
    "default": TenantConfig(
        name="Default",
        enabled_biomarkers=[
            "hemoglobin", "ferritin", "vitamin_d", "vitamin_b12",
            "glucose", "insulin", "tsh", "t4_free", "zinc", "magnesium",
        ],
    ),
    "clinic_premium": TenantConfig(
        name="Clínica Premium",
        ai_model="claude-opus-4-6",
        max_daily_analyses=500,
        enabled_biomarkers=[
            "hemoglobin", "ferritin", "vitamin_d", "vitamin_b12",
            "glucose", "insulin", "tsh", "t4_free", "zinc", "magnesium",
            "cortisol", "testosterone", "estradiol", "crp", "homocysteine",
            "omega3_index", "selenium",
        ],
        report_language="pt-BR",
    ),
    "hospital_basic": TenantConfig(
        name="Hospital Básico",
        ai_model="claude-haiku-4-5-20251001",
        max_daily_analyses=2000,
        enabled_biomarkers=["hemoglobin", "glucose", "vitamin_d", "tsh"],
        include_supplement_recommendations=False,
        include_lifestyle_recommendations=False,
    ),
    "wellness_app": TenantConfig(
        name="Wellness App",
        ai_model="claude-sonnet-4-6",
        max_daily_analyses=10000,
        enabled_biomarkers=[
            "vitamin_d", "vitamin_b12", "ferritin", "zinc", "magnesium",
            "glucose", "tsh", "crp",
        ],
        report_language="en-US",
    ),
}

# ── Faixas de referência padrão (sobrescritíveis por tenant) ──────────────────
STANDARD_REFERENCE_RANGES: Dict[str, BiomarkerRange] = {
    "hemoglobin":   BiomarkerRange(min_normal=12.0, max_normal=17.5, unit="g/dL",     critical_low=7.0),
    "ferritin":     BiomarkerRange(min_normal=15.0, max_normal=300.0, unit="ng/mL",   critical_low=5.0),
    "vitamin_d":    BiomarkerRange(min_normal=30.0, max_normal=100.0, unit="ng/mL",   critical_low=10.0),
    "vitamin_b12":  BiomarkerRange(min_normal=200.0, max_normal=900.0, unit="pg/mL",  critical_low=100.0),
    "glucose":      BiomarkerRange(min_normal=70.0, max_normal=99.0, unit="mg/dL",    critical_low=50.0, critical_high=500.0),
    "insulin":      BiomarkerRange(min_normal=2.0, max_normal=25.0, unit="µUI/mL"),
    "tsh":          BiomarkerRange(min_normal=0.4, max_normal=4.0, unit="µUI/mL"),
    "t4_free":      BiomarkerRange(min_normal=0.8, max_normal=1.8, unit="ng/dL"),
    "zinc":         BiomarkerRange(min_normal=70.0, max_normal=120.0, unit="µg/dL"),
    "magnesium":    BiomarkerRange(min_normal=1.7, max_normal=2.4, unit="mg/dL"),
    "cortisol":     BiomarkerRange(min_normal=6.0, max_normal=23.0, unit="µg/dL"),
    "crp":          BiomarkerRange(min_normal=0.0, max_normal=1.0, unit="mg/L"),
    "homocysteine": BiomarkerRange(min_normal=5.0, max_normal=15.0, unit="µmol/L"),
    "testosterone": BiomarkerRange(min_normal=300.0, max_normal=1000.0, unit="ng/dL"),
    "selenium":     BiomarkerRange(min_normal=70.0, max_normal=150.0, unit="µg/L"),
}


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./nutriai.db"
    anthropic_api_key: str = ""
    allowed_origins: List[str] = ["*"]
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def get_tenant_config(tenant_id: str) -> TenantConfig:
    return TENANT_CONFIGS.get(tenant_id, TENANT_CONFIGS["default"])


def get_reference_range(biomarker: str, tenant_id: str) -> Optional[BiomarkerRange]:
    tenant_cfg = get_tenant_config(tenant_id)
    if biomarker in tenant_cfg.custom_reference_ranges:
        return tenant_cfg.custom_reference_ranges[biomarker]
    return STANDARD_REFERENCE_RANGES.get(biomarker)