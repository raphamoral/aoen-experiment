from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.exam_service import ExamService

router = APIRouter()


class ExamCreate(BaseModel):
    patient_id: str
    exam_date: str                     # YYYY-MM-DD
    lab_name: Optional[str] = None
    biomarkers: dict[str, float]       # {nome_biomarcador: valor}


@router.post("/", status_code=201)
async def create_exam(
    body: ExamCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = request.state.tenant_id
    service = ExamService(db)
    exam = await service.create_exam(
        patient_id=body.patient_id,
        tenant_id=tenant_id,
        exam_date=body.exam_date,
        biomarkers=body.biomarkers,
        lab_name=body.lab_name,
    )
    return {
        "id": exam.id,
        "patient_id": exam.patient_id,
        "tenant_id": exam.tenant_id,
        "exam_date": exam.exam_date,
        "lab_name": exam.lab_name,
        "biomarker_count": len(exam.biomarkers),
        "status": exam.status.value,
        "created_at": exam.created_at.isoformat(),
    }


@router.post("/{exam_id}/analyze")
async def analyze_exam(
    exam_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Aciona o núcleo isolado (core/analyzer.py) para análise clínica.
    Resultado é persistido — custo de análise pago uma única vez.
    """
    tenant_id = request.state.tenant_id
    service = ExamService(db)
    try:
        analysis = await service.analyze_exam(exam_id, tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return {
        "analysis_id": analysis.id,
        "exam_id": analysis.exam_id,
        "overall_score": analysis.overall_score,
        "deficiency_count": len(analysis.deficiencies),
        "excess_count": len(analysis.excesses),
        "deficiencies": analysis.deficiencies,
        "excesses": analysis.excesses,
        "risk_scores": analysis.risk_scores,
        "flags": analysis.flags,
        "created_at": analysis.created_at.isoformat(),
    }


@router.get("/patient/{patient_id}")
async def list_patient_exams(
    patient_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = request.state.tenant_id
    service = ExamService(db)
    exams = await service.get_patient_exams(patient_id, tenant_id)
    return [
        {
            "id": e.id,
            "exam_date": e.exam_date,
            "lab_name": e.lab_name,
            "status": e.status.value,
            "biomarker_count": len(e.biomarkers),
            "created_at": e.created_at.isoformat(),
        }
        for e in exams
    ]


@router.get("/{exam_id}")
async def get_exam(
    exam_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = request.state.tenant_id
    service = ExamService(db)
    exam = await service.get_exam_by_id(exam_id, tenant_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return {
        "id": exam.id,
        "patient_id": exam.patient_id,
        "exam_date": exam.exam_date,
        "lab_name": exam.lab_name,
        "biomarkers": exam.biomarkers,
        "status": exam.status.value,
        "created_at": exam.created_at.isoformat(),
    }