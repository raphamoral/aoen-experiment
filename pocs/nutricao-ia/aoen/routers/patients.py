import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Patient

router = APIRouter()


class PatientCreate(BaseModel):
    name: str
    email: str
    birth_date: str   # YYYY-MM-DD
    sex: str          # M ou F
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None


class PatientResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: str
    birth_date: str
    sex: str
    weight_kg: Optional[float]
    height_cm: Optional[float]
    created_at: str


@router.post("/", response_model=PatientResponse, status_code=201)
async def create_patient(
    body: PatientCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = request.state.tenant_id
    patient = Patient(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        name=body.name,
        email=body.email,
        birth_date=body.birth_date,
        sex=body.sex.upper(),
        weight_kg=body.weight_kg,
        height_cm=body.height_cm,
    )
    db.add(patient)
    await db.flush()
    return PatientResponse(
        id=patient.id,
        tenant_id=patient.tenant_id,
        name=patient.name,
        email=patient.email,
        birth_date=patient.birth_date,
        sex=patient.sex,
        weight_kg=patient.weight_kg,
        height_cm=patient.height_cm,
        created_at=patient.created_at.isoformat(),
    )


@router.get("/")
async def list_patients(request: Request, db: AsyncSession = Depends(get_db)):
    tenant_id = request.state.tenant_id
    result = await db.execute(
        select(Patient)
        .where(Patient.tenant_id == tenant_id)
        .order_by(Patient.created_at.desc())
    )
    return [
        {
            "id": p.id,
            "name": p.name,
            "email": p.email,
            "birth_date": p.birth_date,
            "sex": p.sex,
            "created_at": p.created_at.isoformat(),
        }
        for p in result.scalars().all()
    ]


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    tenant_id = request.state.tenant_id
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id, Patient.tenant_id == tenant_id)
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse(
        id=patient.id,
        tenant_id=patient.tenant_id,
        name=patient.name,
        email=patient.email,
        birth_date=patient.birth_date,
        sex=patient.sex,
        weight_kg=patient.weight_kg,
        height_cm=patient.height_cm,
        created_at=patient.created_at.isoformat(),
    )