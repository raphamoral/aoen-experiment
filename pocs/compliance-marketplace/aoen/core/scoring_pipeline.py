"""
FASE 1 (NÚCLEO): pipeline de ranking de múltiplos candidatos.

Recebe lista de candidatos e retorna top-N rankeados.
Agnóstico de banco de dados — opera sobre dicts.
"""

from typing import List, Dict, Any
from core.compliance_engine import ComplianceMatchInput, run_compliance_match


def rank_candidates(
    project: Dict[str, Any],
    freelancers: List[Dict[str, Any]],
    config: Dict[str, Any],
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    """
    Para cada freelancer candidato, executa o compliance engine e filtra
    pelos elegíveis, retornando os top-N por score.
    """
    results = []

    for freelancer in freelancers:
        inputs = ComplianceMatchInput(
            freelancer_areas=freelancer.get("compliance_areas", []),
            freelancer_jurisdictions=freelancer.get("jurisdictions", []),
            freelancer_certifications=freelancer.get("certifications", []),
            freelancer_years_experience=freelancer.get("years_experience", 0),
            freelancer_reputation_score=freelancer.get("reputation_score", 5.0),
            required_areas=project.get("required_areas", []),
            required_jurisdictions=project.get("required_jurisdictions", []),
            required_certifications=project.get("required_certifications", []),
            config=config,
        )
        output = run_compliance_match(inputs)

        if output.is_eligible:
            results.append({
                "freelancer_id": freelancer["id"],
                "total_score": output.total_score,
                "score_breakdown": output.breakdown,
                "reasoning": output.reasoning,
            })

    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results[:max_results]