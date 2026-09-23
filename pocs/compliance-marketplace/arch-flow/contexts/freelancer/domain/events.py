from dataclasses import dataclass
from shared.kernel.domain_event import DomainEvent


@dataclass
class FreelancerRegistered(DomainEvent):
    """Evento: novo freelancer registrado, aguardando aprovação editorial."""
    freelancer_id: str = ""
    user_id: str = ""
    full_name: str = ""
    event_type: str = "FreelancerRegistered"


@dataclass
class FreelancerApproved(DomainEvent):
    """Evento: freelancer aprovado pela equipe de compliance da plataforma."""
    freelancer_id: str = ""
    reviewer_id: str = ""
    event_type: str = "FreelancerApproved"


@dataclass
class SpecializationAdded(DomainEvent):
    """Evento: nova área regulatória adicionada ao perfil do freelancer."""
    freelancer_id: str = ""
    specialization_code: str = ""
    event_type: str = "SpecializationAdded"