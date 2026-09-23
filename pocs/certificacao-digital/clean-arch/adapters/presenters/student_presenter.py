from entities.student import Student
from adapters.schemas.student_schema import StudentResponse


class StudentPresenter:

    @staticmethod
    def to_response(student: Student) -> StudentResponse:
        return StudentResponse(
            id=student.id,
            name=student.name,
            email=student.email,
        )