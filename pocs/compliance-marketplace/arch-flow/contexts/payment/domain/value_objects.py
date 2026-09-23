from dataclasses import dataclass
from shared.kernel.value_object import ValueObject


@dataclass(frozen=True)
class Money(ValueObject):
    """Valor monetário com moeda explícita."""
    amount: float
    currency: str = "BRL"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Valor monetário não pode ser negativo")


@dataclass(frozen=True)
class PaymentMethod(ValueObject):
    """
    Método de pagamento.

    Maturidade Wardley: COMMODITY
    Em produção: adaptadores para Stripe, Pagar.me, PagSeguro.
    Anti-Corruption Layer isola o domínio das APIs externas.
    """
    type: str     # pix, boleto, credit_card, wire_transfer
    provider: str = "pagar_me"


@dataclass(frozen=True)
class PlatformFee(ValueObject):
    """
    Taxa da plataforma (modelo de receita).

    10% sobre contratos — padrão de marketplace.
    Configurável por tier de cliente em versões futuras.
    """
    percentage: float = 0.10

    def calculate(self, gross_amount: float) -> float:
        return round(gross_amount * self.percentage, 2)

    def net_amount(self, gross_amount: float) -> float:
        return round(gross_amount - self.calculate(gross_amount), 2)