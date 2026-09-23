import logging
from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from shared.events.event_bus import event_bus
from contexts.laboratory.domain.entities import Biomarker, LabResult
from contexts.laboratory.domain.value_objects import (
    BiomarkerValue,
    MeasurementUnit,
    ReferenceRange,
)
from contexts.laboratory.infrastructure.repository import LabResultRepository

logger = logging.getLogger(__name__)


class LabResultIngestionService:
    """Serviço de Ingestão de Resultados Laboratoriais.

    Orquestra o processo de recebimento, estruturação e publicação
    de eventos de um novo exame laboratorial.

    Pertence ao fluxo principal de valor (stream-aligned team):
    é a porta de entrada do sistema; sem exame, não há análise.
    """

    def __init__(self, repository: LabResultRepository) -> None:
        self._repo = repository

    async def ingest(
        self,
        user_id: UUID,
        collection_date: date,
        laboratory_name: str,
        biomarker_data: List[Dict],
    ) -> LabResult:
        lab_result = LabResult.create(
            user_id=user_id,
            collection_date=collection_date,
            laboratory_name=laboratory_name,
        )

        for data in biomarker_data:
            unit = MeasurementUnit(data["unit"])
            biomarker = Biomarker(
                name=data["name"],
                value=BiomarkerValue(numeric_value=data["value"], unit=unit),
                reference_range=ReferenceRange(
                    minimum=data["reference_min"],
                    maximum=data["reference_max"],
                    unit=unit,
                ),
                is_critical=data.get("is_critical", False),
            )
            lab_result.add_biomarker(biomarker)

        lab_result.mark_as_processed()
        self._repo.save(lab_result)

        for event in lab_result.pull_domain_events():
            await event_bus.publish(event)

        logger.info(
            "Exame %s ingerido para usuário %s — %d biomarcadores, %d alterados",
            lab_result.id,
            user_id,
            len(lab_result.biomarkers),
            len(lab_result.altered_biomarkers),
        )
        return lab_result

    def get_by_id(self, lab_result_id: UUID) -> Optional[LabResult]:
        return self._repo.find_by_id(lab_result_id)

    def list_by_user(self, user_id: UUID) -> List[LabResult]:
        return self._repo.find_by_user(user_id)