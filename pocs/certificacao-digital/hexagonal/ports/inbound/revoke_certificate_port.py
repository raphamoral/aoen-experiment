from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RevokeCertificateCommand:
    certificate_id: str
    reason: str


class RevokeCertificatePort(ABC):
    @abstractmethod
    def revoke_certificate(self, command: RevokeCertificateCommand) -> None:
        ...