from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from shared.kernel.aggregate import AggregateRoot
from .value_objects import Certification, ComplianceSpecialization, HourlyRate, Jurisdiction
from .events import FreelancerRegistered, FreelancerApproved, SpecializationAdded


class FreelancerStatus(str, Enum):
    PENDING_REVIEW = "pending_review"   # Aguardando validação pela plataforma
    ACTIVE = "active"                   # Visível e disponível para matching
    SUSPENDED = "suspended"             # Suspenso por violação regulatória/termos
    INACTIVE = "inactive"               # Inativo por escolha do próprio freelancer


@dataclass
class FreelancerProfile(AggregateRoot):
    """
    FreelancerProfile — Aggregate Root do contexto de Freelancer.

    Maturidade Wardley: CUSTOM
    Principal diferencial competitivo: perfil especializado em compliance
    com validação editorial, certificações e jurisdições regulatórias.

    Ubiquitous Language:
    - Freelancer       = profissional autônomo em compliance regulatório
    - Especialização   = área regulatória de expertise declarada
    - Certificação     = credencial profissional validável externamente
    - Jurisdição       = âmbito regulatório geográfico de atuação
    - Aprovação        = validação editorial da plataforma antes do go-live
    """
    user_id: str = ""
    full_name: str = ""
    headline: str = ""   # Ex: "Especialista LGPD & GDPR | 10 anos BACEN"
    bio: str = ""
    hourly_rate: Optional[HourlyRate] = None
    specializations: List[ComplianceSpecialization] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)
    jurisdictions: List[Jurisdiction] = field(default_factory=list)
    status: FreelancerStatus = FreelancerStatus.PENDING_REVIEW
    years_of_experience: int = 0
    availability_hours_per_week: int = 0
    max_complexity_level: int = 1   # Maturidade máxima dos frameworks que domina (1–4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None

    @classmethod
    def register(
        cls,
        user_id: str,
        full_name: str,
        headline: str,
        bio: str,
        hourly_rate: HourlyRate,
        years_of_experience: int,
        availability_hours_per_week: int,
        max_complexity_level: int = 1,
    ) -> "FreelancerProfile":
        """Factory method — registra novo freelancer pendente de aprovação."""
        profile = cls(
            user_id=user_id,
            full_name=full_name,
            headline=headline,
            bio=bio,
            hourly_rate=hourly_rate,
            years_of_experience=years_of_experience,
            availability_hours_per_week=availability_hours_per_week,
            max_complexity_level=max_complexity_level,
        )
        profile.add_domain_event(
            FreelancerRegistered(
                aggregate_id=profile.id,
                freelancer_id=profile.id,
                user_id=user_id,
                full_name=full_name,
            )
        )
        return profile

    def approve(self, reviewer_id: str) -> None:
        """Aprovação editorial — torna o perfil visível para clientes."""
        if self.status != FreelancerStatus.PENDING_REVIEW:
            raise ValueError("Somente perfis em revisão podem ser aprovados")
        self.status = FreelancerStatus.ACTIVE
        self.approved_at = datetime.utcnow()
        self.add_domain_event(
            FreelancerApproved(
                aggregate_id=self.id,
                freelancer_id=self.id,
                reviewer_id=reviewer_id,
            )
        )

    def add_specialization(self, specialization: ComplianceSpecialization) -> None:
        """Adiciona área de especialização regulatória ao perfil."""
        if specialization not in self.specializations:
            self.specializations.append(specialization)
            self.add_domain_event(
                SpecializationAdded(
                    aggregate_id=self.id,
                    freelancer_id=self.id,
                    specialization_code=specialization.code,
                )
            )

    def add_certification(self, certification: Certification) -> None:
        """Registra certificação profissional verificável."""
        if certification not in self.certifications:
            self.certifications.append(certification)

    def add_jurisdiction(self, jurisdiction: Jurisdiction) -> None:
        """Define jurisdição de atuação regulatória."""
        if jurisdiction not in self.jurisdictions:
            self.jurisdictions.append(jurisdiction)

    def suspend(self, reason: str) -> None:
        """Suspende freelancer por violação de termos ou conduta regulatória."""
        self.status = FreelancerStatus.SUSPENDED