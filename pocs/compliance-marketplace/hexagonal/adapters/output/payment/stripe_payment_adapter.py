import logging
import uuid
from decimal import Decimal

from ports.output.payment_port import EscrowResult, IPaymentPort, ReleaseResult

logger = logging.getLogger(__name__)


class StripePaymentAdapter(IPaymentPort):
    """
    Driven adapter de pagamento via Stripe Connect.
    Os métodos contêm stubs documentados — substitua pelas chamadas
    reais do stripe-python SDK. Para trocar por PagSeguro ou MercadoPago,
    implemente IPaymentPort e reconecte no main.py. Zero mudanças no domínio.
    """

    def __init__(self, api_key: str, platform_fee_percent: float = 5.0) -> None:
        self._api_key = api_key
        self._fee = platform_fee_percent

    def create_escrow(
        self,
        contract_id: str,
        amount: Decimal,
        currency: str,
        client_payment_method: str,
    ) -> EscrowResult:
        # Produção: stripe.PaymentIntent.create(
        #     amount=int(amount * 100),
        #     currency=currency.lower(),
        #     payment_method=client_payment_method,
        #     capture_method="manual",
        #     confirm=True,
        # )
        logger.info("Criando escrow para contrato %s: %s %s", contract_id, currency, amount)
        reference_id = f"pi_{uuid.uuid4().hex[:24]}"
        return EscrowResult(
            reference_id=reference_id,
            status="requires_capture",
            amount=amount,
            currency=currency,
        )

    def release_escrow(self, reference_id: str, freelancer_account: str) -> ReleaseResult:
        # Produção: stripe.PaymentIntent.capture(reference_id)
        # depois: stripe.Transfer.create(destination=freelancer_account, ...)
        logger.info("Liberando escrow %s para %s", reference_id, freelancer_account)
        net = (Decimal("1") - Decimal(str(self._fee / 100)))
        return ReleaseResult(
            reference_id=reference_id,
            status="succeeded",
            released_to=freelancer_account,
            net_amount=net,
        )

    def refund_escrow(self, reference_id: str, reason: str) -> bool:
        # Produção: stripe.Refund.create(payment_intent=reference_id, reason=reason)
        logger.info("Estornando escrow %s. Motivo: %s", reference_id, reason)
        return True