from dataclasses import dataclass
from uuid import UUID

from entities.certificate import Certificate
from use_cases.ports.certificate_repository import CertificateRepository
from use_cases.ports.course_repository import CourseRepository
from use_cases.ports.student_repository import StudentRepository


@dataclass
class IssueCertificateInput:
    student_id: UUID
    course_id: UUID
    issuer_id: UUID


@dataclass
class IssueCertificateOutput:
    certificate: Certificate


class IssueCertificateUseCase:
    def __init__(
        self,
        certificate_repo: CertificateRepository,
        course_repo: CourseRepository,
        student_repo: StudentRepository,
    ) -> None:
        self._cert_repo = certificate_repo
        self._course_repo = course_repo
        self._student_repo = student_repo

    def execute(self, data: IssueCertificateInput) -> IssueCertificateOutput:
        student = self._student_repo.find_by_id(data.student_id)
        if not student:
            raise ValueError(f"Student '{data.student_id}' not found")

        course = self._course_repo.find_by_id(data.course_id)
        if not course:
            raise ValueError(f"Course '{data.course_id}' not found")

        if course.issuer_id != data.issuer_id:
            raise ValueError("Issuer does not own this course")

        certificate = Certificate(
            student_id=data.student_id,
            course_id=data.course_id,
            issuer_id=data.issuer_id,
        )
        saved = self._cert_repo.save(certificate)
        return IssueCertificateOutput(certificate=saved)