from dataclasses import dataclass
from enum import Enum
from typing import List

from shared.kernel.value_object import ValueObject


class RiskLevel(str, Enum):
    """Nível de Risco — classificação do impacto clínico do insight.

    Orienta a urgência da recomendação e a prioridade de notificação.
    """

    CRITICAL = "critico"
    HIGH = "alto"
    MODERATE = "moderado"
    LOW = "baixo"
    INFORMATIONAL = "informativo"


class InsightCategory(str, Enum):
    """Categoria do Insight de Saúde — sistema orgânico afetado."""

    CARDIOVASCULAR = "cardiovascular"
    METABOLIC = "metabolico"
    HORMONAL = "hormonal"
    NUTRITIONAL = "nutricional"
    INFLAMMATORY = "inflamatorio"
    RENAL = "renal"
    HEPATIC = "hepatico"
    IMMUNE = "imune"


@dataclass(frozen=True)
class HealthInsight(ValueObject):
    """Insight de Saúde — conhecimento clínico derivado pela IA.

    Representa uma correlação identificada entre biomarcadores,
    traduzida em linguagem compreensível com recomendação acionável.

    Core differentiator: posicionado em Genesis no Wardley Map.
    A qualidade dos insights é o principal valor percebido pelo usuário.
    O Anti-Corruption Layer (llm_gateway) garante que detalhes do LLM
    não vazem para este objeto de valor do domínio.
    """

    title: str
    description: str
    risk_level: RiskLevel
    category: InsightCategory
    biomarkers_involved: List[str]
    recommendation: str
    evidence_basis: str = ""

    def is_actionable(self) -> bool:
        return (
            bool(self.recommendation)
            and self.risk_level != RiskLevel.INFORMATIONAL
        )