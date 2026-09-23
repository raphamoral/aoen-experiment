"""Endpoints de exames laboratoriais."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import LabExamCreate, LabExamOut
from app.services.exam_service import create_exam, get_exam, list_exams
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=LabExamOut, status_code=status.HTTP_201_CREATED)
async def upload_exam(
    payload: LabExamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_exam(db, current_user.id, payload)


@router.get("/", response_model=list[LabExamOut])
async def get_exams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_exams(db, current_user.id)


@router.get("/{exam_id}", response_model=LabExamOut)
async def get_exam_by_id(
    exam_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = await get_exam(db, exam_id, current_user.id)
    if not exam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exame não encontrado")
    return exam