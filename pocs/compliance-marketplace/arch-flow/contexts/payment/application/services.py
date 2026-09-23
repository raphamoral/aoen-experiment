from typing import Optional

from ..domain.entities import Payment
from ..infrastructure.repository import PaymentRepository


class PaymentService:
    """
    Application Service de Pagamento.

    Maturidade Wardley: COMMODITY
    Orquestra a integração com provider externo de pagamento.
    Em produção: injetar cliente Stripe/Pagar.me como dependência.
    """

    def __init__(self, repository: PaymentRepository) -> None:
        self._repository = repository

    async def initiate_payment(
        self,
        contract_id: str,
        payer_id: str,
        payee_id: str,
        gross_amount: float,
        method_type: str,
    ) -> Payment:
        payment = Payment.initiate(
            contract_id=contract_id,
            payer_id=payer_id,
            payee_id=payee_id,
            gross_amount=gross_amount,
            method_type=method_type,
        )
        # Em produção: external_id = await stripe_client.create_charge(...)
        external_id = f"mock_ext_{payment.id[:8]}"
        payment.mark_processing(external_id)
        await self._repository.save(payment)
        return payment

    async def confirm_payment(self, payment_id: str) -> Payment:
        """
        Confirma pagamento — chamado pelo webhook do provider externo.
        Em produção: validar assinatura do webhook antes de confirmar.
        """
        payment = await self._get_or_raise(payment_id)
        payment.mark_completed()
        await self._repository.save(payment)
        return payment

    async def fail_payment(self, payment_id: str) -> Payment:
        payment = await self._get_or_raise(payment_id)
        payment.mark_failed()
        await self._repository.save(payment)
        return payment

    async def find_by_id(self, payment_id: str) -> Optional[Payment]:
        return await self._repository.find_by_id(payment_id)

    async def find_by_contract(self, contract_id: str) -> Optional[Payment]:
        return await self._repository.find_by_contract(contract_id)

    async def _get_or_raise(self, payment_id: str) -> Payment:
        payment = await self._repository.find_by_id(payment_id)
        if not payment:
            raise ValueError(f"Pagamento '{payment_id}' não encontrado")
        return payment