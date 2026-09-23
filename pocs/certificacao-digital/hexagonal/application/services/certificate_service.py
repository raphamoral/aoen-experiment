import uuid
from datetime import datetime
from typing import Optional

from domain.entities.certificate import Certificate
from domain.exceptions import CertificateNotFoundError, DuplicateCertificateError

from ports.inbound.issue_certificate_port import (
    CertificateIssuedResult,
    IssueCertificateCommand,
    IssueCertificatePort,
)
from ports.inbound.list_certificates_port import (
    CertificateSummary,
    ListCertificatesPort,
    ListCertificatesResult,
)
from ports.inbound.revoke_certificate_port import (
    RevokeCertificateCommand,
    RevokeCertificatePort,
)
from ports.inbound.verify_certificate_port import (
    VerificationResult,
    VerifyCertificatePort,
)
from ports.outbound.certificate_repository_port import CertificateRepositoryPort
from ports.outbound.certificate_storage_port import CertificateStoragePort
from ports.outbound.hashing_service_port import HashingServicePort
from ports.outbound.notification_service_port import (
    CertificateIssuedNotification,
    NotificationServicePort,
)


class CertificateApplicationService(
    IssueCertificatePort,
    VerifyCertificatePort,
    RevokeCertificatePort,
    ListCertificatesPort,
):
    """
    Application service — the hexagon itself.

    Implements every inbound port (use case) and depends exclusively on
    outbound port abstractions.  No adapter, framework, or I/O technology
    leaks into this class.
    """

    def __init__(
        self,
        repository: CertificateRepositoryPort,
        hashing_service: HashingServicePort,
        notification_service: NotificationServicePort,
        storage: CertificateStoragePort,
        base_url: str,
    ) -> None:
        self._repository = repository
        self._hashing = hashing_service
        self._notification = notification_service
        self._storage = storage
        self._base_url = base_url

    # ------------------------------------------------------------------
    # IssueCertificatePort
    # ------------------------------------------------------------------

    def issue_certificate(self, command: IssueCertificateCommand) -> CertificateIssuedResult:
        existing = self._repository.find_active_by_student_and_course(
            command.student_id, command.course_id
        )
        if existing:
            raise DuplicateCertificateError(command.student_id, command.course_id)

        certificate_id = str(uuid.uuid4())
        issued_at = datetime.utcnow()

        certificate_hash = self._hashing.hash_certificate_data(
            certificate_id=certificate_id,
            student_id=command.student_id,
            course_id=command.course_id,
            issued_at=issued_at.isoformat(),
            issuer_name=command.issuer_name,
        )

        certificate = Certificate(
            id=certificate_id,
            student_id=command.student_id,
            course_id=command.course_id,
            student_name=command.student_name,
            course_name=command.course_name,
            issuer_name=command.issuer_name,
            duration_hours=command.duration_hours,
            issued_at=issued_at,
            certificate_hash=certificate_hash,
        )

        self._repository.save(certificate)

        self._storage.store_certificate(
            certificate_id=certificate_id,
            student_name=command.student_name,
            course_name=command.course_name,
            issuer_name=command.issuer_name,
            duration_hours=command.duration_hours,
            issued_at=issued_at.isoformat(),
            certificate_hash=certificate_hash,
        )

        verification_url = f"{self._base_url}/api/v1/verify/{certificate_hash}"

        self._notification.notify_certificate_issued(
            CertificateIssuedNotification(
                recipient_email=command.student_email,
                recipient_name=command.student_name,
                course_name=command.course_name,
                certificate_id=certificate_id,
                certificate_hash=certificate_hash,
                verification_url=verification_url,
            )
        )

        return CertificateIssuedResult(
            certificate_id=certificate_id,
            certificate_hash=certificate_hash,
            issued_at=issued_at,
            verification_url=verification_url,
        )

    # ------------------------------------------------------------------
    # VerifyCertificatePort
    # ------------------------------------------------------------------

    def verify_by_hash(self, certificate_hash: str) -> VerificationResult:
        cert = self._repository.find_by_hash(certificate_hash)
        return self._to_verification_result(cert)

    def verify_by_id(self, certificate_id: str) -> VerificationResult:
        cert = self._repository.find_by_id(certificate_id)
        return self._to_verification_result(cert)

    # ------------------------------------------------------------------
    # RevokeCertificatePort
    # ------------------------------------------------------------------

    def revoke_certificate(self, command: RevokeCertificateCommand) -> None:
        cert = self._repository.find_by_id(command.certificate_id)
        if cert is None:
            raise CertificateNotFoundError(command.certificate_id)

        cert.revoke(command.reason)
        self._repository.update(cert)

    # ------------------------------------------------------------------
    # ListCertificatesPort
    # ------------------------------------------------------------------

    def list_by_student(self, student_id: str) -> ListCertificatesResult:
        certs = self._repository.find_by_student_id(student_id)
        summaries = [self._to_summary(c) for c in certs]
        return ListCertificatesResult(certificates=summaries, total=len(summaries))

    def get_by_id(self, certificate_id: str) -> Optional[CertificateSummary]:
        cert = self._repository.find_by_id(certificate_id)
        return self._to_summary(cert) if cert else None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _to_verification_result(self, cert: Optional[Certificate]) -> VerificationResult:
        if cert is None:
            return VerificationResult(is_valid=False)
        return VerificationResult(
            is_valid=cert.is_valid,
            certificate_id=cert.id,
            student_name=cert.student_name,
            course_name=cert.course_name,
            issuer_name=cert.issuer_name,
            duration_hours=cert.duration_hours,
            issued_at=cert.issued_at,
            revocation_reason=cert.revocation_reason,
        )

    def _to_summary(self, cert: Certificate) -> CertificateSummary:
        return CertificateSummary(
            id=cert.id,
            course_name=cert.course_name,
            issuer_name=cert.issuer_name,
            duration_hours=cert.duration_hours,
            issued_at=cert.issued_at,
            is_valid=cert.is_valid,
            certificate_hash=cert.certificate_hash,
        )