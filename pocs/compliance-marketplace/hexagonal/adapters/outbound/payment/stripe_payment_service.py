import logging
from decimal import Decimal

from ports.outbound.payment_service import IPaymentService

logger = logging.getLogger(__name__)


class StripePaymentService(IPaymentService):
    """
    Adaptador de saída: direciona pagamentos via Stripe API.

    Em produção, configure STRIPE_SECRET_KEY como variável de ambiente
    e use `stripe.PaymentIntent.create(...)`.

    O domínio nunca conhece Stripe — apenas IPaymentService.
    Esta implementação é um stub para permitir execução local.
    """

    def __init__(self, api_key: str = "sk_test_stub") -> None:
        self._api_key = api_key

    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        metadata: dict,
    ) -> str:
        intent_id = f"pi_stub_{metadata.get('project_id', 'unknown')}"
        logger.info(
            "[Stripe] create_payment_intent amount=%s %s metadata=%s → %s",
            amount,
            currency,
            metadata,
            intent_id,
        )
        return intent_id

    def release_payment(self, payment_intent_id: str) -> bool:
        logger.info("[Stripe] release_payment %s → OK", payment_intent_id)
        return True

    def refund(self, payment_intent_id: str) -> bool:
        logger.info("[Stripe] refund %s → OK", payment_intent_id)
        return True