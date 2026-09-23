from typing import List
from .value_objects import MatchScore, ProjectRequirement


class ComplianceMatchingAlgorithm:
    """
    Algoritmo de Matching para Compliance Regulatório.

    Maturidade Wardley: GENESIS
    Core inovação da plataforma — lógica proprietária de correspondência
    baseada em frameworks regulatórios, jurisdições e seniority.

    Evolução prevista no mapa Wardley:
    GENESIS → CUSTOM: quando tivermos dados históricos suficientes.
    CUSTOM → PRODUCT: quando o modelo ML for treinado e validado.

    Pesos calibrados com especialistas em compliance:
    - Framework alignment (40%): mais crítico — expertise na norma específica
    - Jurisdiction match (20%): normas nacionais têm especificidades locais
    - Seniority fit (20%): complexidade regulatória exige experiência proporcional
    - Availability fit (10%): disponibilidade operacional
    - Certification bonus (10%): credenciais profissionais como sinal de qualidade
    """

    WEIGHTS = {
        "framework_alignment": 0.40,
        "jurisdiction_match": 0.20,
        "seniority_fit": 0.20,
        "availability_fit": 0.10,
        "certification_bonus": 0.10,
    }

    def calculate_score(
        self,
        requirement: ProjectRequirement,
        freelancer_frameworks: List[str],
        freelancer_jurisdictions: List[str],
        freelancer_experience_years: int,
        freelancer_weekly_hours: int,
        freelancer_max_complexity: int,
        freelancer_certifications: List[str],
    ) -> MatchScore:
        framework_alignment = self._score_framework_alignment(
            list(requirement.framework_codes), freelancer_frameworks
        )
        jurisdiction_match = self._score_jurisdiction(
            list(requirement.jurisdiction_codes), freelancer_jurisdictions
        )
        seniority_fit = self._score_seniority(
            requirement.min_experience_years,
            freelancer_experience_years,
            requirement.complexity_level,
            freelancer_max_complexity,
        )
        availability_fit = self._score_availability(
            requirement.weekly_hours_needed, freelancer_weekly_hours
        )
        certification_bonus = self._score_certifications(
            list(requirement.required_certifications), freelancer_certifications
        )

        total = (
            framework_alignment * self.WEIGHTS["framework_alignment"]
            + jurisdiction_match * self.WEIGHTS["jurisdiction_match"]
            + seniority_fit * self.WEIGHTS["seniority_fit"]
            + availability_fit * self.WEIGHTS["availability_fit"]
            + certification_bonus * self.WEIGHTS["certification_bonus"]
        )

        return MatchScore(
            value=round(min(total, 1.0), 4),
            framework_alignment=round(framework_alignment, 4),
            jurisdiction_match=round(jurisdiction_match, 4),
            seniority_fit=round(seniority_fit, 4),
            availability_fit=round(availability_fit, 4),
            certification_bonus=round(certification_bonus, 4),
        )

    def _score_framework_alignment(
        self, required: List[str], available: List[str]
    ) -> float:
        if not required:
            return 1.0
        matched = sum(1 for f in required if f in available)
        return matched / len(required)

    def _score_jurisdiction(
        self, required: List[str], available: List[str]
    ) -> float:
        if not required:
            return 1.0
        matched = sum(1 for j in required if j in available)
        return matched / len(required)

    def _score_seniority(
        self,
        min_years: int,
        freelancer_years: int,
        required_complexity: int,
        freelancer_complexity: int,
    ) -> float:
        experience_score = (
            min(freelancer_years / max(min_years, 1), 1.0) if min_years > 0 else 1.0
        )
        complexity_score = (
            1.0
            if freelancer_complexity >= required_complexity
            else freelancer_complexity / required_complexity
        )
        return experience_score * 0.6 + complexity_score * 0.4

    def _score_availability(self, needed: int, available: int) -> float:
        if needed == 0:
            return 1.0
        return min(available / needed, 1.0)

    def _score_certifications(
        self, required: List[str], available: List[str]
    ) -> float:
        if not required:
            return 1.0
        matched = sum(1 for c in required if c in available)
        return matched / len(required)