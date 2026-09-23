from dataclasses import dataclass

from entities.student import Student
from use_cases.ports.student_repository import StudentRepository


@dataclass
class RegisterStudentInput:
    name: str
    email: str


@dataclass
class RegisterStudentOutput:
    student: Student


class RegisterStudentUseCase:
    def __init__(self, student_repo: StudentRepository) -> None:
        self._student_repo = student_repo

    def execute(self, data: RegisterStudentInput) -> RegisterStudentOutput:
        existing = self._student_repo.find_by_email(data.email)
        if existing:
            raise ValueError(f"Email '{data.email}' is already registered")

        student = Student(name=data.name, email=data.email)
        saved = self._student_repo.save(student)
        return RegisterStudentOutput(student=saved)