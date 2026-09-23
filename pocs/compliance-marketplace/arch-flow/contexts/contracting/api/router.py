from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from ..application.services import ContractingService
from ..infrastructure.repository import ContractRepository

router = APIRouter(prefix="/contracts", tags=["Contracting (Product)"])

_repository = ContractRepository()
_service = ContractingService(_repository)


class CreateContractRequest(BaseModel):
    client_id: str
    freelancer_id: str
    match_id: str
    amount_brl: float
    start_date: datetime
    end_date: datetime


class AddDeliverableRequest(BaseModel):
    title: str
    description: str
    estimated_hours: int
    framework_code: str


class SignRequest(BaseModel):
    signer_role: str   # "client" ou "freelancer"


class DeliverableResponse(BaseModel):
    title: str
    framework_code: str
    estimated_hours: int
    description: str


class ContractResponse(BaseModel):
    id: str
    client_id: str
    freelancer_id: str
    match_id: str
    status: str
    amount_brl: Optional[float]
    deliverables: List[DeliverableResponse]
    client_signed_at: Optional[datetime]
    freelancer_signed_at: Optional[datetime]
    completed_at: Optional[datetime]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ContractResponse)
async def create_contract(request: CreateContractRequest):
    """Cria contrato rascunho entre cliente e freelancer (a partir de match aceito)."""
    contract = await _service.create_contract(**request.model_dump())
    return _to_response(contract)


@router.post("/{contract_id}/deliverables", response_model=ContractResponse)
async def add_deliverable(contract_id: str, request: AddDeliverableRequest):
    """Adiciona entregável de compliance ao escopo do contrato."""
    try:
        contract = await _service.add_deliverable(contract_id, **request.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return _to_response(contract)


@router.patch("/{contract_id}/submit")
async def submit_for_signature(contract_id: str):
    """Envia contrato para assinatura digital das partes."""
    try:
        contract = await _service.submit_for_signature(contract_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return _to_response(contract)


@router.patch("/{contract_id}/sign", response_model=ContractResponse)
async def sign_contract(contract_id: str, request: SignRequest):
    """Registra assinatura digital (cliente ou freelancer)."""
    try:
        contract = await _service.sign_contract(contract_id, request.signer_role)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return _to_response(contract)


@router.patch("/{contract_id}/complete", response_model=ContractResponse)
async def complete_contract(contract_id: str):
    """Conclui contrato após aprovação dos entregáveis — dispara liberação de pagamento."""
    try:
        contract = await _service.complete_contract(contract_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return _to_response(contract)


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(contract_id: str):
    contract = await _service.find_by_id(contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado"
        )
    return _to_response(contract)


@router.get("/by-client/{client_id}", response_model=List[ContractResponse])
async def list_contracts_by_client(client_id: str):
    contracts = await _service.find_by_client(client_id)
    return [_to_response(c) for c in contracts]


def _to_response(contract) -> dict:
    return {
        "id": contract.id,
        "client_id": contract.client_id,
        "freelancer_id": contract.freelancer_id,
        "match_id": contract.match_id,
        "status": contract.status.value,
        "amount_brl": contract.value.amount if contract.value else None,
        "deliverables": [
            {
                "title": d.title,
                "framework_code": d.framework_code,
                "estimated_hours": d.estimated_hours,
                "description": d.description,
            }
            for d in contract.deliverables
        ],
        "client_signed_at": contract.client_signed_at,
        "freelancer_signed_at": contract.freelancer_signed_at,
        "completed_at": contract.completed_at,
    }