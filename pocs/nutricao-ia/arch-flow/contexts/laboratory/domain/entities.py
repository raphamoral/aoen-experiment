from dataclasses import dataclass, field
from datetime import date
from typing import List
from uuid import UUID

from shared.kernel.aggregate_root import AggregateRoot
from shared.kernel.entity import Entity
from contexts.laboratory.domain.value_objects import BiomarkerValue, ReferenceRange
from contexts.laboratory.domain.events import BiomarkerOutOfRange, LabResultReceived


@dataclass
class Biomarker(Entity):
    """Biomarcador — parâmetro bioquímico medido no exame laboratorial.

    Linguagem ubíqua: representa um marcador biológico específico
    (ex: Hemoglobina, Vitamina D, TSH, Ferritina) com seu valor,
    unidade e faixa de referência para classificação clínica.
    """

    name: str
    value: BiomarkerValue
    reference_range: ReferenceRange
    is_critical: bool = False

    @property
    def status(self) -> str:
        if self.value.is_within_range(self.reference_range):
            return "normal"
        deviation = abs(
            self.reference_range.deviation_percentage(self.value.numeric_value)
        )
        return "critico" if deviation > 50 else "alterado"

    @property
    def is_out_of_range(self) -> bool:
        return not self.value.is_within_range(self.reference_range)


@dataclass
class LabResult(AggregateRoot):
    """Resultado Laboratorial — agregado raiz do contexto laboratorial.

    Representa o conjunto completo de biomarcadores de um exame,
    garantindo consistência transacional de toda a análise.

    Wardley: Custom Build — o diferencial está na capacidade de
    interpretar correlações entre biomarcadores; a coleta em si
    tende ao commodity (integração com APIs de laboratórios).

    Team Topologies: Stream-aligned — pertence ao fluxo principal
    de valor junto com o contexto de AI Analysis.
    """

    user_id: UUID
    collection_date: date
    laboratory_name: str
    biomarkers: List[Biomarker] = field(default_factory=list)
    is_processed: bool = False

    @classmethod
    def create(
        cls,
        user_id: UUID,
        collection_date: date,
        laboratory_name: str,
    ) -> "LabResult":
        result = cls(
            user_id=user_id,
            collection_date=collection_date,
            laboratory_name=laboratory_name,
        )
        result.record_event(
            LabResultReceived(
                lab_result_id=result.id,
                user_id=user_id,
                collection_date=collection_date,
            )
        )
        return result

    def add_biomarker(self, biomarker: Biomarker) -> None:
        self.biomarkers.append(biomarker)
        if biomarker.is_out_of_range:
            self.record_event(
                BiomarkerOutOfRange(
                    lab_result_id=self.id,
                    user_id=self.user_id,
                    biomarker_name=biomarker.name,
                    value=biomarker.value.numeric_value,
                    status=biomarker.status,
                )
            )

    def mark_as_processed(self) -> None:
        self.is_processed = True

    @property
    def critical_biomarkers(self) -> List[Biomarker]:
        return [b for b in self.biomarkers if b.status == "critico"]

    @property
    def altered_biomarkers(self) -> List[Biomarker]:
        return [b for b in self.biomarkers if b.is_out_of_range]