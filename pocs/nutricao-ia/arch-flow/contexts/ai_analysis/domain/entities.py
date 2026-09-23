from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID

from shared.kernel.aggregate_root import AggregateRoot
from contexts.ai_analysis.domain.value_objects import HealthInsight, RiskLevel
from contexts.ai_analysis.domain.events import AnalysisGenerated, CriticalInsightFound


@dataclass
class PersonalizedAnalysis(AggregateRoot):
    """Análise Personalizada — agregado raiz do contexto de IA.

    Encapsula o raciocínio clínico da IA sobre os biomarcadores,
    produzindo insights acionáveis personalizados para o paciente.

    Wardley: Genesis → Custom.
    A interpretação por IA de exames para nutrição é emergente mas
    se consolida rapidamente; é o núcleo da proposta de valor.

    Team Topologies: Complicated Subsystem Team.
    Requer expertise especializada em IA + clínica + nutrição.
    Não deve ser responsabilidade do stream-aligned team diretamente.
    """

    user_id: UUID
    lab_result_id: UUID
    generated_at: datetime
    insights: List[HealthInsight] = field(default_factory=list)
    summary: str = ""
    raw_llm_response: str = ""
    model_used: str = ""

    @classmethod
    def create(
        cls,
        user_id: UUID,
        lab_result_id: UUID,
        model_used: str,
    ) -> "PersonalizedAnalysis":
        return cls(
            user_id=user_id,
            lab_result_id=lab_result_id,
            generated_at=datetime.utcnow(),
            model_used=model_used,
        )

    def add_insight(self, insight: HealthInsight) -> None:
        self.insights.append(insight)
        if insight.risk_level == RiskLevel.CRITICAL:
            self.record_event(
                CriticalInsightFound(
                    analysis_id=self.id,
                    user_id=self.user_id,
                    insight_title=insight.title,
                    risk_level=insight.risk_level.value,
                )
            )

    def finalize(self, summary: str, raw_response: str) -> None:
        self.summary = summary
        self.raw_llm_response = raw_response
        self.record_event(
            AnalysisGenerated(
                analysis_id=self.id,
                user_id=self.user_id,
                lab_result_id=self.lab_result_id,
                insight_count=len(self.insights),
                has_critical=any(
                    i.risk_level == RiskLevel.CRITICAL for i in self.insights
                ),
            )
        )

    @property
    def critical_insights(self) -> List[HealthInsight]:
        return [i for i in self.insights if i.risk_level == RiskLevel.CRITICAL]

    @property
    def actionable_insights(self) -> List[HealthInsight]:
        return [i for i in self.insights if i.is_actionable()]