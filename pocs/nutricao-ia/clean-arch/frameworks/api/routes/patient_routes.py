from fastapi import APIRouter, Depends, HTTPException

from adapters.controllers.patient_controller import PatientController, RegisterPatientRequest
from frameworks.api.schemas.patient_schema import PatientCreateSchema
from frameworks.container import get_patient_controller

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("/", status_code=201)
def register_patient(
    body: PatientCreateSchema,
    controller: PatientController = Depends(get_patient_controller),
):
    try:
        return controller.register(
            RegisterPatientRequest(
                name=body.name,
                birth_date=body.birth_date,
                gender=body.gender,
                weight_kg=body.weight_kg,
                height_cm=body.height_cm,
                email=str(body.email),
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{patient_id}/report")
def get_patient_report(
    patient_id: str,
    controller: PatientController = Depends(get_patient_controller),
):
    try:
        return controller.get_report(patient_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))