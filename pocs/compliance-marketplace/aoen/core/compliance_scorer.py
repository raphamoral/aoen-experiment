"""
AOEN FASE 1 — NÚCLEO DIFERENCIADOR

Motor de pontuação de compliance: calcula a afinidade entre um freelancer
e um projeto com base em dimensões específicas do domínio regulatório.

Isolado de framework, banco e HTTP — testável e portável.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FreelancerProfile:
    domains: list[str]
    certifications: list[str]
    regulations_experience: dict[str, int]  # {domain: anos}
    hourly_rate: float
    rating: float
    portfolio_score: float


@dataclass
class ProjectRequirements:
    required_domains: list[str]
    required_certifications: list[str]
    budget_max: float | None
    estimated_hours: int | None
    urgency_level: int  # 1-5


@dataclass
class ScoreBreakdown:
    domain_overlap: float = 0.0
    certification_match: float = 0.0
    experience_years: float = 0.0
    rating: float = 0.0
    rate_fit: float = 0.0
    total: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


def score_freelancer(
    freelancer: FreelancerProfile,
    project: ProjectRequirements,
    weights: dict[str, float],
) -> ScoreBreakdown:
    breakdown = ScoreBreakdown()

    # --- Dimensão 1: sobreposição de domínios ---
    if project.required_domains:
        matched = set(freelancer.domains) & set(project.required_domains)
        breakdown.domain_overlap = len(matched) / len(project.required_domains)
        breakdown.details["matched_domains"] = list(matched)
    else:
        breakdown.domain_overlap = 1.0

    # --- Dimensão 2: certificações ---
    if project.required_certifications:
        matched_certs = set(freelancer.certifications) & set(project.required_certifications)
        breakdown.certification_match = len(matched_certs) / len(project.required_certifications)
        breakdown.details["matched_certifications"] = list(matched_certs)
    else:
        breakdown.certification_match = 1.0

    # --- Dimensão 3: anos de experiência nos domínios exigidos ---
    if project.required_domains and freelancer.regulations_experience:
        total_years = sum(
            freelancer.regulations_experience.get(d, 0)
            for d in project.required_domains
        )
        avg_years = total_years / len(project.required_domains)
        # Normaliza: 5+ anos = score máximo
        breakdown.experience_years = min(avg_years / 5.0, 1.0)
        breakdown.details["avg_experience_years"] = round(avg_years, 2)
    else:
        breakdown.experience_years = 0.5

    # --- Dimensão 4: rating do freelancer ---
    breakdown.rating = freelancer.rating / 5.0 if freelancer.rating else 0.5

    # --- Dimensão 5: adequação de taxa ao orçamento ---
    if project.budget_max and project.estimated_hours:
        max_rate = project.budget_max / project.estimated_hours
        if freelancer.hourly_rate <= max_rate:
            # Quanto mais próximo do teto sem ultrapassar, melhor (evita dumping)
            breakdown.rate_fit = min(freelancer.hourly_rate / max_rate + 0.1, 1.0)
        else:
            breakdown.rate_fit = 0.0
        breakdown.details["max_budget_rate"] = round(max_rate, 2)
    else:
        breakdown.rate_fit = 0.7  # sem orçamento definido, neutro positivo

    # --- Score final ponderado ---
    breakdown.total = round(
        breakdown.domain_overlap * weights.get("domain_overlap", 0.35)
        + breakdown.certification_match * weights.get("certification_match", 0.25)
        + breakdown.experience_years * weights.get("experience_years", 0.20)
        + breakdown.rating * weights.get("rating", 0.15)
        + breakdown.rate_fit * weights.get("rate_fit", 0.05),
        4,
    )

    return breakdown