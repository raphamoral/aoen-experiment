from fastapi import APIRouter, Depends, HTTPException, status

from adapters.input.http.schemas import (
    ExamResultInput,
    ExamResultResponse,
    LabExamResponse,
    SubmitLabExamRequest,
)
from domain.exceptions import DomainValidationError, PatientNotFoundError
from ports.input.submit_lab_exam_use_case import (
    ExamResultInput as DomainExamResultInput,
    SubmitLabExamCommand,
    SubmitLabExamUseCasePort,
)
from config.dependencies import get_submit_lab_exam_use_case

router = APIRouter(prefix="/lab-exams", tags=["lab-exams"])


def _map_result(r: ExamResultInput) -> DomainExamResultInput:
    return DomainExamResultInput(
        exam_type=r.exam_type,
        value=r.value,
        unit=r.unit,
        reference_min=r.reference_min,
        reference_max=r.reference_max,
    )


@router.post(
    "/",
    response_model=LabExamResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_lab_exam(
    body: SubmitLabExamRequest,
    use_case: SubmitLabExamUseCasePort = Depends(get_submit_lab_exam_use_case),
) -> LabExamResponse:
    try:
        exam = await use_case.execute(
            SubmitLabExamCommand(
                patient_id=body.patient_id,
                exam_date=body.exam_date,
                results=[_map_result(r) for r in body.results],
            )
        )
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except DomainValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return LabExamResponse(
        id=exam.id,
        patient_id=exam.patient_id,
        exam_date=exam.exam_date,
        results=[
            ExamResultResponse(
                exam_type=r.exam_type,
                value=r.value,
                unit=r.unit,
                reference_min=r.reference_min,
                reference_max=r.reference_max,
                is_normal=r.is_normal,
            )
            for r in exam.results
        ],
        created_at=exam.created_at,
    )