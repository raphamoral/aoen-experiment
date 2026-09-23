from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.dependencies import get_exam_service

router = APIRouter()


class ExamResultIn(BaseModel):
    marker_name: str
    value: float
    unit: str | None = None
    reference_min: float | None = None
    reference_max: float | None = None


class ExamPanelCreate(BaseModel):
    user_id: int
    exam_date: datetime
    lab_name: str | None = None
    notes: str | None = None
    results: list[ExamResultIn]


class ExamResultOut(BaseModel):
    id: int
    marker_name: str
    value: float
    unit: str | None
    reference_min: float | None
    reference_max: float | None
    status: str

    model_config = {"from_attributes": True}


class ExamPanelOut(BaseModel):
    id: int
    user_id: int
    exam_date: datetime
    lab_name: str | None
    notes: str | None
    results: list[ExamResultOut]

    model_config = {"from_attributes": True}


@router.post("/", response_model=ExamPanelOut, status_code=201)
async def create_exam_panel(payload: ExamPanelCreate, service=Depends(get_exam_service)):
    return await service.register_panel(
        user_id=payload.user_id,
        exam_date=payload.exam_date,
        lab_name=payload.lab_name or "",
        notes=payload.notes or "",
        results=[r.model_dump() for r in payload.results],
    )


@router.get("/{panel_id}", response_model=ExamPanelOut)
async def get_exam_panel(panel_id: int, service=Depends(get_exam_service)):
    panel = await service.get_panel(panel_id)
    if not panel:
        raise HTTPException(status_code=404, detail="Painel de exames não encontrado")
    return panel


@router.get("/", response_model=list[ExamPanelOut])
async def list_user_exams(user_id: int, service=Depends(get_exam_service)):
    return await service.list_user_panels(user_id)


@router.get("/{panel_id}/deficiencies")
async def analyze_deficiencies(panel_id: int, service=Depends(get_exam_service)):
    result = await service.analyze_deficiencies(panel_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result