"""
FASE 1 (NÚCLEO / VALOR): motor de matching de compliance.

Este módulo é o diferenciador central do produto. Ele encapsula todo o
conhecimento de domínio sobre como avaliar a adequação de um freelancer
a um projeto de compliance regulatório.

Isolamento intencional:
- Sem imports de SQLAlchemy, FastAPI ou qualquer framework web.
- Entrada e saída são dicts puros — testável standalone e portável.
- FASE 4: pode ser movido para processo/serviço separado sem alterar contratos.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


# Grafo de adjacência de áreas de compliance (similaridade de domínio).
# Se um freelancer tem LGPD, ele entende parcialmente GDPR e vice-versa.
COMPLIANCE_ADJACENCY: Dict[str, List[str]] = {
    "lgpd":     ["gdpr", "iso_27001"],
    "gdpr":     ["lgpd", "iso_27001"],
    "sox":      ["cvm", "aml"],
    "pci_dss":  ["iso_27001", "bacen"],
    "iso_27001": ["lgpd", "gdpr", "pci_dss"],
    "bacen":    ["pci_dss", "cvm", "aml"],
    "cvm":      ["sox", "bacen", "aml"],
    "anvisa":   [],
    "aml":      ["bacen", "cvm", "sox"],
    "esg":      [],
}

ADJACENCY_PARTIAL_CREDIT = 0.4  # crédito parcial por área adjacente


@dataclass
class ComplianceMatchInput:
    freelancer_areas: List[str]
    freelancer_jurisdictions: List[str]
    freelancer_certifications: List[Dict[str, Any]]
    freelancer_years_experience: int
    freelancer_reputation_score: float
    required_areas: List[str]
    required_jurisdictions: List[str]
    required_certifications: List[str]
    config: Dict[str, Any]  # tenant matching config


@dataclass
class ComplianceMatchOutput:
    total_score: float
    breakdown: Dict[str, float] = field(default_factory=dict)
    is_eligible: bool = False
    reasoning: Dict[str, Any] = field(default_factory=dict)


def score_area_coverage(
    freelancer_areas: List[str],
    required_areas: List[str],
) -> tuple[float, Dict[str, Any]]:
    """
    Score de cobertura de áreas com crédito parcial por adjacência.
    Retorna (score 0-1, detalhes).
    """
    if not required_areas:
        return 1.0, {"covered": [], "partial": [], "missing": []}

    covered, partial, missing = [], [], []

    for area in required_areas:
        if area in freelancer_areas:
            covered.append(area)
        elif any(area in COMPLIANCE_ADJACENCY.get(fa, []) for fa in freelancer_areas):
            partial.append(area)
        else:
            missing.append(area)

    total = len(required_areas)
    score = (len(covered) + len(partial) * ADJACENCY_PARTIAL_CREDIT) / total

    return min(score, 1.0), {
        "covered": covered,
        "partial_credit": partial,
        "missing": missing,
        "raw_coverage_pct": round(score * 100, 1),
    }


def score_jurisdiction_match(
    freelancer_jurisdictions: List[str],
    required_jurisdictions: List[str],
) -> tuple[float, Dict[str, Any]]:
    if not required_jurisdictions:
        return 1.0, {"matched": [], "missing": []}

    matched = [j for j in required_jurisdictions if j in freelancer_jurisdictions]
    missing = [j for j in required_jurisdictions if j not in freelancer_jurisdictions]
    score = len(matched) / len(required_jurisdictions)

    return score, {"matched": matched, "missing": missing}


def score_certifications(
    freelancer_certifications: List[Dict[str, Any]],
    required_certifications: List[str],
) -> tuple[float, Dict[str, Any]]:
    if not required_certifications:
        return 1.0, {"matched": [], "missing": []}

    cert_names = {c.get("name", "").lower() for c in freelancer_certifications}
    matched = [c for c in required_certifications if c.lower() in cert_names]
    missing = [c for c in required_certifications if c.lower() not in cert_names]

    score = len(matched) / len(required_certifications) if required_certifications else 1.0

    return score, {"matched": matched, "missing": missing}


def score_experience(years: int, normalization_max: int) -> float:
    return min(years / max(normalization_max, 1), 1.0)


def run_compliance_match(inputs: ComplianceMatchInput) -> ComplianceMatchOutput:
    """
    Ponto de entrada do núcleo. Executa o pipeline completo de scoring.
    Contrato estável — a implementação interna pode evoluir sem quebrar callers.
    """
    weights = inputs.config.get("weights", {})
    exp_max = inputs.config.get("experience_normalization_max", 15)
    threshold = inputs.config.get("min_score_threshold", 0.60)

    area_score, area_detail = score_area_coverage(
        inputs.freelancer_areas, inputs.required_areas
    )
    juris_score, juris_detail = score_jurisdiction_match(
        inputs.freelancer_jurisdictions, inputs.required_jurisdictions
    )
    cert_score, cert_detail = score_certifications(
        inputs.freelancer_certifications, inputs.required_certifications
    )
    exp_score = score_experience(inputs.freelancer_years_experience, exp_max)
    rep_score = inputs.freelancer_reputation_score / 10.0  # normaliza 0-10 → 0-1

    total = (
        area_score   * weights.get("area_coverage", 0.35)
        + juris_score  * weights.get("jurisdiction_match", 0.25)
        + cert_score   * weights.get("certification_bonus", 0.20)
        + exp_score    * weights.get("experience_score", 0.10)
        + rep_score    * weights.get("reputation_score", 0.10)
    )
    total = round(total, 4)

    breakdown = {
        "area_coverage":       round(area_score, 4),
        "jurisdiction_match":  round(juris_score, 4),
        "certification_bonus": round(cert_score, 4),
        "experience_score":    round(exp_score, 4),
        "reputation_score":    round(rep_score, 4),
    }
    reasoning = {
        "areas":         area_detail,
        "jurisdictions": juris_detail,
        "certifications": cert_detail,
        "years_experience": inputs.freelancer_years_experience,
        "reputation_raw":  inputs.freelancer_reputation_score,
    }

    return ComplianceMatchOutput(
        total_score=total,
        breakdown=breakdown,
        is_eligible=total >= threshold,
        reasoning=reasoning,
    )