from abc import ABC, abstractmethod


class CertificateStoragePort(ABC):
    @abstractmethod
    def store_certificate(
        self,
        certificate_id: str,
        student_name: str,
        course_name: str,
        issuer_name: str,
        duration_hours: int,
        issued_at: str,
        certificate_hash: str,
    ) -> str:
        """Persist the certificate artifact. Returns its storage path or URL."""
        ...

    @abstractmethod
    def delete_certificate(self, certificate_id: str) -> None:
        ...