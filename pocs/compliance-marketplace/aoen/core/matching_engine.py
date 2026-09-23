"""
AOEN FASE 1 + FASE 4 — NÚCLEO ISOLADO

Orquestra o scoring de múltiplos freelancers para um projeto.
Processo isolável: pode rodar como worker separado para medir custo por tenant.
"""

from dataclasses import dataclass

from core.compliance_scorer import (
    FreelancerProfile,
    ProjectRequirements,
    ScoreBreakdown,
    score_freelancer,
)


@dataclass
class MatchCandidate:
    freelancer_id: str
    score: float
    breakdown: ScoreBreakdown


def run_matching(
    project: ProjectRequirements,
    freelancers: list[tuple[str, FreelancerProfile]],
    weights: dict[str, float],
    top_n: int = 10,
    min_score: float = 0.0,
) -> list[MatchCandidate]:
    """
    Executa o matching para um projeto.

    Retorna os top_n freelancers acima de min_score, ordenados por score desc.
    Puro: sem IO, sem efeitos colaterais — auditável e testável unitariamente.
    """
    candidates: list[MatchCandidate] = []

    for freelancer_id, profile in freelancers:
        breakdown = score_freelancer(profile, project, weights)
        if breakdown.total >= min_score:
            candidates.append(
                MatchCandidate(
                    freelancer_id=freelancer_id,
                    score=breakdown.total,
                    breakdown=breakdown,
                )
            )

    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates[:top_n]