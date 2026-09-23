from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from shared.kernel.aggregate import AggregateRoot
from .value_objects import ContractPeriod, ContractValue, DeliverableScope
from .events import ContractCreated, ContractSigned, ContractCompleted


class ContractStatus(str, Enum):
    DRAFT = "draft"                         # Em edição pelo cliente
    PENDING_SIGNATURES = "pending_signatures"  # Enviado para assinatura
    ACTIVE = "active"                       # Assinado — em execução
    COMPLETED = "completed"                 # Entregáveis aprovados
    CANCELLED = "cancelled"                 # Cancelado antes de assinar
    DISPUTED = "disputed"                   # Em litígio regulatório/comercial


@dataclass
class Contract(AggregateRoot):
    """
    Contract — Aggregate Root do contexto de Contratação.

    Maturidade Wardley: PRODUCT
    Em produção: integrar com ClickSign ou DocuSign para assinatura digital
    via Anti-Corruption Layer. O domínio conhece apenas "assinar", não o provider.

    Ubiquitous Language:
    - Contrato    = acordo formal para execução de projeto de compliance
    - Entregável  = produto específico e mensurável do trabalho regulatório
    - Vigência    = período de execução acordado entre as partes
    - Assinatura  = aceite digital com validade jurídica (MP 2.200-2/2001)
    """
    client_id: str = ""
    freelancer_id: str = ""
    match_id: str = ""          # Rastreabilidade: originado de qual match?
    value: Optional[ContractValue] = None
    period: Optional[ContractPeriod] = None
    deliverables: List[DeliverableScope] = field(default_factory=list)
    status: ContractStatus = ContractStatus.DRAFT
    client_signed_at: Optional[datetime] = None
    freelancer_signed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        client_id: str,
        freelancer_id: str,
        match_id: str,
        value: ContractValue,
        period: ContractPeriod,
    ) -> "Contract":
        """Factory method — cria contrato rascunho a partir de match aceito."""
        contract = cls(
            client_id=client_id,
            freelancer_id=freelancer_id,
            match_id=match_id,
            value=value,
            period=period,
        )
        contract.add_domain_event(
            ContractCreated(
                aggregate_id=contract.id,
                contract_id=contract.id,
                client_id=client_id,
                freelancer_id=freelancer_id,
            )
        )
        return contract

    def add_deliverable(self, deliverable: DeliverableScope) -> None:
        """Adiciona entregável de compliance ao escopo do contrato."""
        self.deliverables.append(deliverable)

    def submit_for_signature(self) -> None:
        """Envia contrato para assinatura digital das partes."""
        if not self.deliverables:
            raise ValueError("Contrato deve ter ao menos um entregável definido")
        if self.status != ContractStatus.DRAFT:
            raise ValueError("Somente rascunhos podem ser enviados para assinatura")
        self.status = ContractStatus.PENDING_SIGNATURES

    def sign_as_client(self) -> None:
        """Registra assinatura digital do cliente."""
        if self.status != ContractStatus.PENDING_SIGNATURES:
            raise ValueError("Contrato não está aguardando assinatura")
        self.client_signed_at = datetime.utcnow()
        self._check_fully_signed()

    def sign_as_freelancer(self) -> None:
        """Registra assinatura digital do freelancer."""
        if self.status != ContractStatus.PENDING_SIGNATURES:
            raise ValueError("Contrato não está aguardando assinatura")
        self.freelancer_signed_at = datetime.utcnow()
        self._check_fully_signed()

    def _check_fully_signed(self) -> None:
        if self.client_signed_at and self.freelancer_signed_at:
            self.status = ContractStatus.ACTIVE
            self.add_domain_event(
                ContractSigned(
                    aggregate_id=self.id,
                    contract_id=self.id,
                    client_id=self.client_id,
                    freelancer_id=self.freelancer_id,
                )
            )

    def complete(self) -> None:
        """Conclui contrato após aprovação dos entregáveis — libera pagamento."""
        if self.status != ContractStatus.ACTIVE:
            raise ValueError("Somente contratos ativos podem ser concluídos")
        self.status = ContractStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.add_domain_event(
            ContractCompleted(
                aggregate_id=self.id,
                contract_id=self.id,
                total_value_brl=self.value.amount if self.value else 0.0,
            )
        )

    def cancel(self) -> None:
        """Cancela contrato antes da assinatura."""
        if self.status not in (ContractStatus.DRAFT, ContractStatus.PENDING_SIGNATURES):
            raise ValueError("Contrato ativo ou concluído não pode ser cancelado")
        self.status = ContractStatus.CANCELLED