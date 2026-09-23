import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from shared.events.event_bus import event_bus
from contexts.ai_analysis.domain.entities import PersonalizedAnalysis
from contexts.ai_analysis.domain.value_objects import (
    HealthInsight,
    InsightCategory,
    RiskLevel,
)
from contexts.ai_analysis.infrastructure.llm_gateway import AnthropicLLMGateway
from contexts.ai_analysis.infrastructure.repository import AnalysisRepository

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-opus-4-6"


class AIAnalysisOrchestrator:
    """Orquestrador de Análise por IA.

    Coordena o fluxo: biomarcadores + contexto do usuário → LLM → insights.
    Aplica o Anti-Corruption Layer entre o domínio e o gateway de IA:
    transforma respostas brutas do LLM em objetos de domínio tipados.

    Team Topologies: Complicated Subsystem — este serviço requer
    expertise especializada em prompt engineering clínico, validação
    de outputs de LLM e interpretação de resultados laboratoriais.
    Não deve ser mantido pelo mesmo time do contexto laboratorial.
    """

    def __init__(
        self,
        repository: AnalysisRepository,
        llm_gateway: AnthropicLLMGateway,
    ) -> None:
        self._repo = repository
        self._llm = llm_gateway

    async def generate_analysis(
        self,
        user_id: UUID,
        lab_result_id: UUID,
        biomarkers: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None,
    ) -> PersonalizedAnalysis:
        analysis = PersonalizedAnalysis.create(
            user_id=user_id,
            lab_result_id=lab_result_id,
            model_used=DEFAULT_MODEL,
        )

        llm_result = self._llm.analyze_biomarkers(
            biomarkers=biomarkers,
            user_context=user_context or {},
        )

        for insight_data in llm_result.get("insights", []):
            try:
                insight = HealthInsight(
                    title=insight_data["title"],
                    description=insight_data["description"],
                    risk_level=RiskLevel(insight_data.get("risk_level", "informativo")),
                    category=InsightCategory(
                        insight_data.get("category", "nutricional")
                    ),
                    biomarkers_involved=insight_data.get("biomarkers_involved", []),
                    recommendation=insight_data.get("recommendation", ""),
                    evidence_basis=insight_data.get("evidence_basis", ""),
                )
                analysis.add_insight(insight)
            except (ValueError, KeyError) as exc:
                logger.warning("Insight ignorado por dados inválidos: %s", exc)

        analysis.finalize(
            summary=llm_result.get("summary", ""),
            raw_response=str(llm_result),
        )

        self._repo.save(analysis)

        for event in analysis.pull_domain_events():
            await event_bus.publish(event)

        logger.info(
            "Análise %s gerada: %d insights (%d críticos) para usuário %s",
            analysis.id,
            len(analysis.insights),
            len(analysis.critical_insights),
            user_id,
        )
        return analysis

    def get_by_id(self, analysis_id: UUID) -> Optional[PersonalizedAnalysis]:
        return self._repo.find_by_id(analysis_id)

    def get_by_lab_result(self, lab_result_id: UUID) -> Optional[PersonalizedAnalysis]:
        return self._repo.find_by_lab_result(lab_result_id)

    def list_by_user(self, user_id: UUID) -> List[PersonalizedAnalysis]:
        return self._repo.find_by_user(user_id)