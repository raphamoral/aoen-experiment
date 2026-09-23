from fastapi import APIRouter, Depends, HTTPException

from adapters.controllers.student_controller import StudentController
from adapters.schemas.student_schema import RegisterStudentRequest, StudentResponse
from frameworks.http.dependencies import get_student_controller

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse, status_code=201)
def register_student(
    body: RegisterStudentRequest,
    controller: StudentController = Depends(get_student_controller),
) -> StudentResponse:
    try:
        return controller.register(body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))