from abc import ABC, abstractmethod


class HashingServicePort(ABC):
    @abstractmethod
    def hash_certificate_data(
        self,
        certificate_id: str,
        student_id: str,
        course_id: str,
        issued_at: str,
        issuer_name: str,
    ) -> str:
        """Produce a deterministic, tamper-evident hash from certificate fields."""
        ...