from dataclasses import dataclass
from decimal import Decimal

SUPPORTED_CURRENCIES = {"BRL", "USD", "EUR"}


@dataclass(frozen=True)
class HourlyRate:
    amount: Decimal
    currency: str = "BRL"

    def __post_init__(self) -> None:
        if self.amount <= Decimal("0"):
            raise ValueError("O valor da taxa horária deve ser positivo.")
        if self.currency not in SUPPORTED_CURRENCIES:
            raise ValueError(
                f"Moeda não suportada: {self.currency}. "
                f"Use uma de: {SUPPORTED_CURRENCIES}"
            )

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}/h"