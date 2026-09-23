from dataclasses import dataclass
from uuid import UUID

from entities.course import Course
from use_cases.ports.course_repository import CourseRepository
from use_cases.ports.issuer_repository import IssuerRepository


@dataclass
class RegisterCourseInput:
    name: str
    description: str
    issuer_id: UUID
    workload_hours: int


@dataclass
class RegisterCourseOutput:
    course: Course


class RegisterCourseUseCase:
    def __init__(
        self,
        course_repo: CourseRepository,
        issuer_repo: IssuerRepository,
    ) -> None:
        self._course_repo = course_repo
        self._issuer_repo = issuer_repo

    def execute(self, data: RegisterCourseInput) -> RegisterCourseOutput:
        issuer = self._issuer_repo.find_by_id(data.issuer_id)
        if not issuer:
            raise ValueError(f"Issuer '{data.issuer_id}' not found")

        course = Course(
            name=data.name,
            description=data.description,
            issuer_id=data.issuer_id,
            workload_hours=data.workload_hours,
        )
        saved = self._course_repo.save(course)
        return RegisterCourseOutput(course=saved)