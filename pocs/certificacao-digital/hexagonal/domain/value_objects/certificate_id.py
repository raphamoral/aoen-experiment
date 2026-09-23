import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class CertificateId:
    value: str

    def __post_init__(self) -> None:
        try:
            uuid.UUID(self.value)
        except ValueError:
            raise ValueError(f"Invalid certificate ID format: '{self.value}'")

    @classmethod
    def generate(cls) -> "CertificateId":
        return cls(value=str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value