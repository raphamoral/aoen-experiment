from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CertificateIssuedNotification:
    recipient_email: str
    recipient_name: str
    course_name: str
    certificate_id: str
    certificate_hash: str
    verification_url: str


class NotificationServicePort(ABC):
    @abstractmethod
    def notify_certificate_issued(self, notification: CertificateIssuedNotification) -> None:
        ...

    @abstractmethod
    def notify_certificate_revoked(
        self,
        recipient_email: str,
        recipient_name: str,
        certificate_id: str,
        reason: str,
    ) -> None:
        ...