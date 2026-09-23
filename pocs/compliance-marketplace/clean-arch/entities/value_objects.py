from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class ComplianceSpecialty(str, Enum):
    LGPD = "LGPD"
    GDPR = "GDPR"
    SOX = "SOX"
    PCI_DSS = "PCI-DSS"
    ISO_27001 = "ISO-27001"
    HIPAA = "HIPAA"
    BACEN = "BACEN"
    CVM = "CVM"
    SUSEP = "SUSEP"
    ANTI_CORRUPTION = "ANTI_CORRUPTION"


class ProjectStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ProposalStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not self.value or "@" not in self.value:
            raise ValueError(f"Invalid email address: {self.value}")
        local, domain = self.value.split("@", 1)
        if not local or "." not in domain:
            raise ValueError(f"Invalid email address: {self.value}")


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "BRL"

    def __post_init__(self) -> None:
        if self.amount < Decimal("0"):
            raise ValueError("Money amount cannot be negative")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __ge__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount >= other.amount

    def __le__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount <= other.amount