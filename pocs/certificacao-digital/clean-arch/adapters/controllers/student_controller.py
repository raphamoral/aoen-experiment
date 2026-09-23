from adapters.presenters.student_presenter import StudentPresenter
from adapters.schemas.student_schema import RegisterStudentRequest, StudentResponse
from use_cases.register_student import RegisterStudentInput, RegisterStudentUseCase


class StudentController:
    def __init__(self, register_uc: RegisterStudentUseCase) -> None:
        self._register_uc = register_uc

    def register(self, request: RegisterStudentRequest) -> StudentResponse:
        output = self._register_uc.execute(
            RegisterStudentInput(name=request.name, email=request.email)
        )
        return StudentPresenter.to_response(output.student)