from dataclasses import dataclass


@dataclass
class RegisterFreelancerCommand:
    """Command: registrar novo freelancer na plataforma."""
    user_id: str
    full_name: str
    headline: str
    bio: str
    hourly_rate_brl: float
    years_of_experience: int
    availability_hours_per_week: int
    max_complexity_level: int = 1


@dataclass
class ApproveFreelancerCommand:
    """Command: aprovar perfil após revisão editorial."""
    freelancer_id: str
    reviewer_id: str


@dataclass
class AddSpecializationCommand:
    """Command: adicionar especialização regulatória ao perfil."""
    freelancer_id: str
    specialization_code: str
    specialization_description: str
    regulatory_body: str


@dataclass
class AddCertificationCommand:
    """Command: registrar certificação profissional."""
    freelancer_id: str
    name: str
    issuer: str
    valid_until: str
    credential_url: str = ""