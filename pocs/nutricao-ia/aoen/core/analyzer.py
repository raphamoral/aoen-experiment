"""
FASE 1 — NÚCLEO ISOLADO: Analisador de Biomarcadores Laboratoriais

Sem dependências externas (sem SQLAlchemy, FastAPI, Anthropic SDK).
Recebe dicts Python, devolve dataclasses Python.
Testável de forma completamente isolada.
Extraível para microserviço ou worker sem refatoração.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"
    MILD = "mild"


@dataclass
class BiomarkerDeviation:
    biomarker: str
    value: float
    unit: str
    reference_min: float
    reference_max: float
    deviation_type: str          # "deficiency" | "excess"
    deviation_percent: float
    severity: Severity


@dataclass
class AnalysisResult:
    exam_id: str
    deficiencies: List[BiomarkerDeviation] = field(default_factory=list)
    excesses: List[BiomarkerDeviation] = field(default_factory=list)
    risk_scores: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.0
    flags: List[str] = field(default_factory=list)


# ── Mapa de risco por categoria clínica ──────────────────────────────────────
_RISK_MAP: Dict[str, List[str]] = {
    "metabolic":    ["glucose", "insulin", "hba1c"],
    "thyroid":      ["tsh", "t4_free", "t3_free"],
    "hematologic":  ["hemoglobin", "ferritin", "vitamin_b12", "folate"],
    "inflammatory": ["crp", "homocysteine"],
    "bone_health":  ["vitamin_d", "calcium", "phosphorus", "magnesium"],
    "hormonal":     ["cortisol", "testosterone", "estradiol"],
}

_SEVERITY_WEIGHT = {
    Severity.CRITICAL: 1.0,
    Severity.HIGH:     0.7,
    Severity.MODERATE: 0.4,
    Severity.MILD:     0.2,
}


def _classify_severity(deviation_pct: float) -> Severity:
    if deviation_pct >= 60:
        return Severity.CRITICAL
    if deviation_pct >= 40:
        return Severity.HIGH
    if deviation_pct >= 20:
        return Severity.MODERATE
    return Severity.MILD


def _check_biomarker(
    name: str,
    value: float,
    ref_min: float,
    ref_max: float,
    unit: str,
) -> Optional[BiomarkerDeviation]:
    if ref_min <= value <= ref_max:
        return None

    if value < ref_min:
        pct = ((ref_min - value) / ref_min) * 100
        dev_type = "deficiency"
    else:
        pct = ((value - ref_max) / ref_max) * 100
        dev_type = "excess"

    return BiomarkerDeviation(
        biomarker=name,
        value=value,
        unit=unit,
        reference_min=ref_min,
        reference_max=ref_max,
        deviation_type=dev_type,
        deviation_percent=round(pct, 2),
        severity=_classify_severity(pct),
    )


def _risk_scores(deviations: List[BiomarkerDeviation]) -> Dict[str, float]:
    """Score de risco por categoria clínica: 0.0 (ótimo) — 1.0 (crítico)."""
    by_name = {d.biomarker: d for d in deviations}
    scores: Dict[str, float] = {}

    for category, biomarkers in _RISK_MAP.items():
        hits = [by_name[b] for b in biomarkers if b in by_name]
        if not hits:
            continue
        raw = sum(_SEVERITY_WEIGHT[h.severity] for h in hits)
        scores[category] = round(min(raw / len(biomarkers), 1.0), 3)

    return scores


def _overall_score(
    total_biomarkers: int,
    deviations: List[BiomarkerDeviation],
) -> float:
    """Score de saúde geral: 0 (crítico) — 100 (ótimo)."""
    if total_biomarkers == 0:
        return 0.0
    penalty = sum(_SEVERITY_WEIGHT[d.severity] for d in deviations)
    return round(max(0.0, (total_biomarkers - penalty) / total_biomarkers * 100), 1)


def _clinical_flags(
    biomarkers: Dict[str, float],
    deviations: List[BiomarkerDeviation],
) -> List[str]:
    flags: List[str] = []

    if any(d.severity == Severity.CRITICAL for d in deviations):
        flags.append("CRITICAL_VALUES_PRESENT")

    glucose = biomarkers.get("glucose")
    insulin = biomarkers.get("insulin")
    if glucose and insulin:
        homa_ir = (glucose * insulin) / 405.0
        if homa_ir > 2.5:
            flags.append(f"INSULIN_RESISTANCE_SUSPECTED_HOMA_IR_{homa_ir:.1f}")

    hgb = biomarkers.get("hemoglobin")
    ferritin = biomarkers.get("ferritin")
    if hgb and hgb < 12.0:
        if ferritin and ferritin < 15.0:
            flags.append("IRON_DEFICIENCY_ANEMIA_SUSPECTED")
        else:
            flags.append("ANEMIA_NON_IRON_INVESTIGATE_CAUSE")

    vit_d = biomarkers.get("vitamin_d")
    if vit_d and vit_d < 20.0:
        flags.append("SEVERE_VITAMIN_D_DEFICIENCY")

    tsh = biomarkers.get("tsh")
    if tsh:
        if tsh > 10.0:
            flags.append("HYPOTHYROIDISM_SUSPECTED")
        elif tsh < 0.1:
            flags.append("HYPERTHYROIDISM_SUSPECTED")

    crp = biomarkers.get("crp")
    if crp and crp > 3.0:
        flags.append("CHRONIC_INFLAMMATION_MARKER_ELEVATED")

    return flags


def analyze(
    exam_id: str,
    biomarkers: Dict[str, float],
    reference_ranges: Dict[str, Tuple[float, float, str]],
) -> AnalysisResult:
    """
    Ponto de entrada principal do núcleo.

    Args:
        exam_id: ID do exame
        biomarkers: {nome_biomarcador: valor_numérico}
        reference_ranges: {nome_biomarcador: (min_normal, max_normal, unidade)}

    Returns:
        AnalysisResult com deficiências, excessos, scores e flags clínicos
    """
    deviations: List[BiomarkerDeviation] = []

    for name, value in biomarkers.items():
        if name not in reference_ranges:
            continue
        ref_min, ref_max, unit = reference_ranges[name]
        dev = _check_biomarker(name, value, ref_min, ref_max, unit)
        if dev:
            deviations.append(dev)

    deficiencies = [d for d in deviations if d.deviation_type == "deficiency"]
    excesses = [d for d in deviations if d.deviation_type == "excess"]

    return AnalysisResult(
        exam_id=exam_id,
        deficiencies=deficiencies,
        excesses=excesses,
        risk_scores=_risk_scores(deviations),
        overall_score=_overall_score(len(biomarkers), deviations),
        flags=_clinical_flags(biomarkers, deviations),
    )