from adapters.presenters.course_presenter import CoursePresenter
from adapters.schemas.course_schema import CourseResponse, RegisterCourseRequest
from use_cases.register_course import RegisterCourseInput, RegisterCourseUseCase


class CourseController:
    def __init__(self, register_uc: RegisterCourseUseCase) -> None:
        self._register_uc = register_uc

    def register(self, request: RegisterCourseRequest) -> CourseResponse:
        output = self._register_uc.execute(
            RegisterCourseInput(
                name=request.name,
                description=request.description,
                issuer_id=request.issuer_id,
                workload_hours=request.workload_hours,
            )
        )
        return CoursePresenter.to_response(output.course)