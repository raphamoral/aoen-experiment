from fastapi import APIRouter, Depends, HTTPException

from adapters.controllers.course_controller import CourseController
from adapters.schemas.course_schema import CourseResponse, RegisterCourseRequest
from frameworks.http.dependencies import get_course_controller

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=CourseResponse, status_code=201)
def register_course(
    body: RegisterCourseRequest,
    controller: CourseController = Depends(get_course_controller),
) -> CourseResponse:
    try:
        return controller.register(body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))