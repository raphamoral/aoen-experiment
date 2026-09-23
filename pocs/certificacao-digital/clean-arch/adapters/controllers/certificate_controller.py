from uuid import UUID

from adapters.presenters.certificate_presenter import CertificatePresenter
from adapters.schemas.certificate_schema import (
    CertificateResponse,
    IssueCertificateRequest,
    RevokeCertificateRequest,
    VerificationResponse,
)
from use_cases.issue_certificate import IssueCertificateInput, IssueCertificateUseCase
from use_cases.list_student_certificates import (
    ListStudentCertificatesInput,
    ListStudentCertificatesUseCase,
)
from use_cases.revoke_certificate import RevokeCertificateInput, RevokeCertificateUseCase
from use_cases.verify_certificate import VerifyCertificateInput, VerifyCertificateUseCase


class CertificateController:
    def __init__(
        self,
        issue_uc: IssueCertificateUseCase,
        verify_uc: VerifyCertificateUseCase,
        revoke_uc: RevokeCertificateUseCase,
        list_uc: ListStudentCertificatesUseCase,
    ) -> None:
        self._issue_uc = issue_uc
        self._verify_uc = verify_uc
        self._revoke_uc = revoke_uc
        self._list_uc = list_uc

    def issue(self, request: IssueCertificateRequest) -> CertificateResponse:
        output = self._issue_uc.execute(
            IssueCertificateInput(
                student_id=request.student_id,
                course_id=request.course_id,
                issuer_id=request.issuer_id,
            )
        )
        return CertificatePresenter.to_response(output.certificate)

    def verify(self, verification_hash: str) -> VerificationResponse:
        output = self._verify_uc.execute(
            VerifyCertificateInput(verification_hash=verification_hash)
        )
        return CertificatePresenter.to_verification_response(output.is_valid, output.certificate)

    def revoke(self, certificate_id: UUID, request: RevokeCertificateRequest) -> CertificateResponse:
        output = self._revoke_uc.execute(
            RevokeCertificateInput(
                certificate_id=certificate_id,
                issuer_id=request.issuer_id,
            )
        )
        return CertificatePresenter.to_response(output.certificate)

    def list_by_student(self, student_id: UUID) -> list[CertificateResponse]:
        output = self._list_uc.execute(ListStudentCertificatesInput(student_id=student_id))
        return [CertificatePresenter.to_response(cert) for cert in output.certificates]