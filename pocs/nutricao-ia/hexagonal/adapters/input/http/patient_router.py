from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from adapters.input.http.schemas import PatientResponse, RegisterPatientRequest
from domain.exceptions import DomainValidationError, DuplicateEmailError
from ports.input.register_patient_use_case import (
    RegisterPatientCommand,
    RegisterPatientUseCasePort,
)
from config.dependencies import get_register_patient_use_case

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_patient(
    body: RegisterPatientRequest,
    use_case: RegisterPatientUseCasePort = Depends(get_register_patient_use_case),
) -> PatientResponse:
    try:
        patient = await use_case.execute(
            RegisterPatientCommand(
                name=body.name,
                email=body.email,
                age=body.age,
                gender=body.gender,
                health_goals=body.health_goals,
            )
        )
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except (DomainValidationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return PatientResponse(
        id=patient.id,
        name=patient.name,
        email=patient.email,
        age=patient.age,
        gender=patient.gender,
        health_goals=patient.health_goals,
        created_at=patient.created_at,
    )