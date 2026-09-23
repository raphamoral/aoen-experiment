from dataclasses import dataclass
from uuid import UUID

from entities.certificate import Certificate
from use_cases.ports.certificate_repository import CertificateRepository
from use_cases.ports.student_repository import StudentRepository


@dataclass
class ListStudentCertificatesInput:
    student_id: UUID


@dataclass
class ListStudentCertificatesOutput:
    certificates: list[Certificate]


class ListStudentCertificatesUseCase:
    def __init__(
        self,
        certificate_repo: CertificateRepository,
        student_repo: StudentRepository,
    ) -> None:
        self._cert_repo = certificate_repo
        self._student_repo = student_repo

    def execute(self, data: ListStudentCertificatesInput) -> ListStudentCertificatesOutput:
        student = self._student_repo.find_by_id(data.student_id)
        if not student:
            raise ValueError(f"Student '{data.student_id}' not found")

        certificates = self._cert_repo.find_by_student_id(data.student_id)
        return ListStudentCertificatesOutput(certificates=certificates)