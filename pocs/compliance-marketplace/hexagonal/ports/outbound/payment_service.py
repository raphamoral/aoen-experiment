from abc import ABC, abstractmethod
from decimal import Decimal


class IPaymentService(ABC):
    """
    Porta de saída (driven port) para processamento de pagamentos.
    Retorna identificadores opacos; o domínio nunca vê detalhes de Stripe/PagSeguro.
    """

    @abstractmethod
    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        metadata: dict,
    ) -> str:
        """Cria intenção de pagamento. Retorna payment_intent_id."""
        ...

    @abstractmethod
    def release_payment(self, payment_intent_id: str) -> bool: ...

    @abstractmethod
    def refund(self, payment_intent_id: str) -> bool: ...