from datetime import date
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared.infra.database import get_db
from contexts.laboratory.application.services import LabResultIngestionService
from contexts.laboratory.infrastructure.repository import LabResultRepository

router = APIRouter(prefix="/lab-results", tags=["Resultados Laboratoriais"])


class BiomarkerInput(BaseModel):
    name: str
    value: float
    unit: str
    reference_min: float
    reference_max: float
    is_critical: bool = False


class LabResultInput(BaseModel):
    user_id: UUID
    collection_date: date
    laboratory_name: str
    biomarkers: List[BiomarkerInput]


class BiomarkerOutput(BaseModel):
    id: str
    name: str
    value: float
    unit: str
    status: str
    is_critical: bool


class LabResultOutput(BaseModel):
    id: str
    user_id: str
    collection_date: date
    laboratory_name: str
    biomarkers: List[BiomarkerOutput]
    is_processed: bool
    altered_count: int
    critical_count: int


def get_service(db: Session = Depends(get_db)) -> LabResultIngestionService:
    return LabResultIngestionService(LabResultRepository(db))


@router.post("/", response_model=LabResultOutput, status_code=status.HTTP_201_CREATED)
async def ingest_lab_result(
    payload: LabResultInput,
    service: LabResultIngestionService = Depends(get_service),
):
    """Ingestão de Resultado Laboratorial.

    Recebe o exame completo, processa os biomarcadores e publica
    eventos para os contexts de Nutrição e Análise IA reagirem.
    """
    lab_result = await service.ingest(
        user_id=payload.user_id,
        collection_date=payload.collection_date,
        laboratory_name=payload.laboratory_name,
        biomarker_data=[b.model_dump() for b in payload.biomarkers],
    )
    return _to_output(lab_result)


@router.get("/{lab_result_id}", response_model=LabResultOutput)
def get_lab_result(
    lab_result_id: UUID,
    service: LabResultIngestionService = Depends(get_service),
):
    lab_result = service.get_by_id(lab_result_id)
    if not lab_result:
        raise HTTPException(
            status_code=404, detail="Resultado laboratorial não encontrado"
        )
    return _to_output(lab_result)


@router.get("/user/{user_id}", response_model=List[LabResultOutput])
def list_user_lab_results(
    user_id: UUID,
    service: LabResultIngestionService = Depends(get_service),
):
    return [_to_output(r) for r in service.list_by_user(user_id)]


def _to_output(lab_result) -> LabResultOutput:
    return LabResultOutput(
        id=str(lab_result.id),
        user_id=str(lab_result.user_id),
        collection_date=lab_result.collection_date,
        laboratory_name=lab_result.laboratory_name,
        biomarkers=[
            BiomarkerOutput(
                id=str(b.id),
                name=b.name,
                value=b.value.numeric_value,
                unit=b.value.unit.value,
                status=b.status,
                is_critical=b.is_critical,
            )
            for b in lab_result.biomarkers
        ],
        is_processed=lab_result.is_processed,
        altered_count=len(lab_result.altered_biomarkers),
        critical_count=len(lab_result.critical_biomarkers),
    )