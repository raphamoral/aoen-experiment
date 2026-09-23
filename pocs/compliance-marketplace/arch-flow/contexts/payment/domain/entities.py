from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from shared.kernel.aggregate import AggregateRoot
from .value_objects import Money, PaymentMethod, PlatformFee


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class Payment(AggregateRoot):
    """
    Payment — Aggregate Root do contexto de Pagamento.

    Maturidade Wardley: COMMODITY
    Lógica de negócio mínima — o trabalho real é no provider externo.
    Anti-Corruption Layer adapta: Stripe Charge → Payment (domínio).

    Modelo financeiro:
    - gross_amount: valor total pago pelo cliente
    - platform_fee: 10% retido pela plataforma (receita)
    - net_amount: 90% repassado ao freelancer
    """
    contract_id: str = ""
    payer_id: str = ""      # client_id
    payee_id: str = ""      # freelancer_id
    gross_amount: Optional[Money] = None
    platform_fee: Optional[Money] = None
    net_amount: Optional[Money] = None
    method: Optional[PaymentMethod] = None
    status: PaymentStatus = PaymentStatus.PENDING
    external_payment_id: str = ""   # ID no provider (ex: Stripe charge_id)
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

    @classmethod
    def initiate(
        cls,
        contract_id: str,
        payer_id: str,
        payee_id: str,
        gross_amount: float,
        method_type: str,
    ) -> "Payment":
        """Factory method — inicia pagamento com cálculo automático de taxas."""
        fee_calc = PlatformFee()
        return cls(
            contract_id=contract_id,
            payer_id=payer_id,
            payee_id=payee_id,
            gross_amount=Money(amount=gross_amount),
            platform_fee=Money(amount=fee_calc.calculate(gross_amount)),
            net_amount=Money(amount=fee_calc.net_amount(gross_amount)),
            method=PaymentMethod(type=method_type),
        )

    def mark_processing(self, external_id: str) -> None:
        """Registra ID externo do provider e marca como em processamento."""
        self.status = PaymentStatus.PROCESSING
        self.external_payment_id = external_id

    def mark_completed(self) -> None:
        """Confirma pagamento liquidado — libera repasse ao freelancer."""
        self.status = PaymentStatus.COMPLETED
        self.processed_at = datetime.utcnow()

    def mark_failed(self) -> None:
        self.status = PaymentStatus.FAILED

    def refund(self) -> None:
        if self.status != PaymentStatus.COMPLETED:
            raise ValueError("Somente pagamentos completados podem ser reembolsados")
        self.status = PaymentStatus.REFUNDED