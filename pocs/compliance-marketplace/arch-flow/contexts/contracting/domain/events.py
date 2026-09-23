from dataclasses import dataclass
from shared.kernel.domain_event import DomainEvent


@dataclass
class ContractCreated(DomainEvent):
    """Evento: contrato rascunho criado entre cliente e freelancer."""
    contract_id: str = ""
    client_id: str = ""
    freelancer_id: str = ""
    event_type: str = "ContractCreated"


@dataclass
class ContractSigned(DomainEvent):
    """Evento: contrato assinado digitalmente por ambas as partes — torna-se ativo."""
    contract_id: str = ""
    client_id: str = ""
    freelancer_id: str = ""
    event_type: str = "ContractSigned"


@dataclass
class ContractCompleted(DomainEvent):
    """Evento: contrato concluído com entregáveis aprovados — libera pagamento."""
    contract_id: str = ""
    total_value_brl: float = 0.0
    event_type: str = "ContractCompleted"