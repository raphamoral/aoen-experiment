from typing import Dict, List, Optional

from ..domain.entities import MatchResult
from ..domain.services import ComplianceMatchingAlgorithm
from ..domain.value_objects import ProjectRequirement

# Threshold mínimo de relevância — abaixo disso, o match não é apresentado
RELEVANCE_THRESHOLD = 0.30


class MatchingService:
    """
    Application Service de Matching.

    Orquestra o algoritmo de matching com dados dos contextos
    Freelancer e Compliance Catalog via Anti-Corruption Layer.

    Em produção: os freelancer_profiles viriam de uma query ao contexto
    Freelancer (via API interna ou evento), não do request HTTP diretamente.
    """

    def __init__(self) -> None:
        self._algorithm = ComplianceMatchingAlgorithm()
        self._results: Dict[str, MatchResult] = {}

    async def find_matches(
        self,
        client_id: str,
        requirement: ProjectRequirement,
        freelancer_profiles: List[dict],
    ) -> List[MatchResult]:
        """
        Executa matching e retorna lista ordenada por score descendente.
        Filtra candidatos abaixo do threshold de relevância.
        """
        results = []
        for fp in freelancer_profiles:
            score = self._algorithm.calculate_score(
                requirement=requirement,
                freelancer_frameworks=[
                    s["code"] for s in fp.get("specializations", [])
                ],
                freelancer_jurisdictions=fp.get("jurisdiction_codes", []),
                freelancer_experience_years=fp.get("years_of_experience", 0),
                freelancer_weekly_hours=fp.get("availability_hours_per_week", 0),
                freelancer_max_complexity=fp.get("max_complexity_level", 1),
                freelancer_certifications=[
                    c["name"] for c in fp.get("certifications", [])
                ],
            )
            if score.value >= RELEVANCE_THRESHOLD:
                match = MatchResult(
                    client_id=client_id,
                    project_requirement=requirement,
                    freelancer_id=fp["id"],
                    score=score,
                )
                self._results[match.id] = match
                results.append(match)

        return sorted(results, key=lambda r: r.score.value, reverse=True)

    async def get_result(self, match_id: str) -> Optional[MatchResult]:
        return self._results.get(match_id)

    async def accept_match(self, match_id: str) -> MatchResult:
        match = self._results.get(match_id)
        if not match:
            raise ValueError(f"Match '{match_id}' não encontrado")
        match.accept()
        return match

    async def reject_match(self, match_id: str) -> MatchResult:
        match = self._results.get(match_id)
        if not match:
            raise ValueError(f"Match '{match_id}' não encontrado")
        match.reject()
        return match