from dataclasses import dataclass
from typing import Optional

from entities.certificate import Certificate
from use_cases.ports.certificate_repository import CertificateRepository


@dataclass
class VerifyCertificateInput:
    verification_hash: str


@dataclass
class VerifyCertificateOutput:
    is_valid: bool
    certificate: Optional[Certificate]


class VerifyCertificateUseCase:
    def __init__(self, certificate_repo: CertificateRepository) -> None:
        self._cert_repo = certificate_repo

    def execute(self, data: VerifyCertificateInput) -> VerifyCertificateOutput:
        certificate = self._cert_repo.find_by_hash(data.verification_hash)
        if not certificate:
            return VerifyCertificateOutput(is_valid=False, certificate=None)
        return VerifyCertificateOutput(is_valid=certificate.is_valid, certificate=certificate)