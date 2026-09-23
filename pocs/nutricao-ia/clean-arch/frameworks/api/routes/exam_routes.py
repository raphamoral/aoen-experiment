from fastapi import APIRouter, Depends, HTTPException

from adapters.controllers.exam_controller import ExamController, ExamMarkerRequest, SubmitExamRequest
from frameworks.api.schemas.exam_schema import ExamSubmitSchema
from frameworks.container import get_exam_controller

router = APIRouter(prefix="/patients/{patient_id}/exams", tags=["exams"])


@router.post("/", status_code=201)
def submit_exam(
    patient_id: str,
    body: ExamSubmitSchema,
    controller: ExamController = Depends(get_exam_controller),
):
    try:
        return controller.submit(
            SubmitExamRequest(
                patient_id=patient_id,
                exam_date=body.exam_date,
                lab_name=body.lab_name,
                markers=[
                    ExamMarkerRequest(
                        name=m.name,
                        value=m.value,
                        unit=m.unit,
                        reference_min=m.reference_min,
                        reference_max=m.reference_max,
                    )
                    for m in body.markers
                ],
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))