from dataclasses import dataclass
from uuid import UUID

from entities.certificate import Certificate
from use_cases.ports.certificate_repository import CertificateRepository


@dataclass
class RevokeCertificateInput:
    certificate_id: UUID
    issuer_id: UUID


@dataclass
class RevokeCertificateOutput:
    certificate: Certificate


class RevokeCertificateUseCase:
    def __init__(self, certificate_repo: CertificateRepository) -> None:
        self._cert_repo = certificate_repo

    def execute(self, data: RevokeCertificateInput) -> RevokeCertificateOutput:
        certificate = self._cert_repo.find_by_id(data.certificate_id)
        if not certificate:
            raise ValueError(f"Certificate '{data.certificate_id}' not found")

        if certificate.issuer_id != data.issuer_id:
            raise ValueError("Only the original issuer can revoke this certificate")

        certificate.revoke()  # business rule enforced in the entity
        updated = self._cert_repo.update(certificate)
        return RevokeCertificateOutput(certificate=updated)