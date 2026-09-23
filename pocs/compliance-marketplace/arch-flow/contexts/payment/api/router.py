from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from ..application.services import PaymentService
from ..infrastructure.repository import PaymentRepository

router = APIRouter(prefix="/payments", tags=["Payment (Commodity)"])

_repository = PaymentRepository()
_service = PaymentService(_repository)


class InitiatePaymentRequest(BaseModel):
    contract_id: str
    payer_id: str
    payee_id: str
    gross_amount: float
    method_type: str = "pix"   # pix | boleto | credit_card | wire_transfer


class PaymentResponse(BaseModel):
    id: str
    contract_id: str
    status: str
    gross_amount: Optional[float]
    platform_fee: Optional[float]
    net_amount: Optional[float]
    method_type: Optional[str]
    external_payment_id: str


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PaymentResponse)
async def initiate_payment(request: InitiatePaymentRequest):
    """Inicia cobrança para contrato de compliance concluído."""
    payment = await _service.initiate_payment(**request.model_dump())
    return _to_response(payment)


@router.patch("/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(payment_id: str):
    """
    Confirma pagamento liquidado (chamado por webhook do provider).
    Em produção: proteger com validação de assinatura HMAC do provider.
    """
    try:
        payment = await _service.confirm_payment(payment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _to_response(payment)


@router.patch("/{payment_id}/fail")
async def fail_payment(payment_id: str):
    """Registra falha no pagamento (chamado por webhook do provider)."""
    try:
        payment = await _service.fail_payment(payment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return _to_response(payment)


@router.get("/by-contract/{contract_id}", response_model=PaymentResponse)
async def get_payment_by_contract(contract_id: str):
    payment = await _service.find_by_contract(contract_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pagamento não encontrado"
        )
    return _to_response(payment)


def _to_response(payment) -> dict:
    return {
        "id": payment.id,
        "contract_id": payment.contract_id,
        "status": payment.status.value,
        "gross_amount": payment.gross_amount.amount if payment.gross_amount else None,
        "platform_fee": payment.platform_fee.amount if payment.platform_fee else None,
        "net_amount": payment.net_amount.amount if payment.net_amount else None,
        "method_type": payment.method.type if payment.method else None,
        "external_payment_id": payment.external_payment_id,
    }