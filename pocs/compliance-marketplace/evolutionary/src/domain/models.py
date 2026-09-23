"""
Modelos de domínio puros — sem dependência de ORM ou framework.

ADR-002: Domain puro separado da persistência.
Decisão reversível: persistência pode mudar (SQLite → Postgres → DynamoDB)
sem afetar regras de negócio.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4


class ComplianceArea(str, enum.Enum):
    GDPR = "GDPR"
    LGPD = "LGPD"
    SOX = "SOX"
    PCI_DSS = "PCI_DSS"
    ISO_27001 = "ISO_27001"
    HIPAA = "HIPAA"
    BACEN = "BACEN"
    CVM = "CVM"
    SUSEP = "SUSEP"


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProposalStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


@dataclass
class Certification:
    name: str
    issuer: str
    issued_at: datetime
    expires_at: Optional[datetime] = None
    verified: bool = False


@dataclass
class Freelancer:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    email: str = ""
    bio: str = ""
    areas: List[ComplianceArea] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)
    hourly_rate_brl: float = 0.0
    reputation_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_eligible_for(self, area: ComplianceArea) -> bool:
        return area in self.areas

    def add_certification(self, cert: Certification) -> None:
        self.certifications.append(cert)

    def update_reputation(self, new_rating: float) -> None:
        if not (1.0 <= new_rating <= 5.0):
            raise ValueError("Rating deve estar entre 1.0 e 5.0")
        total = self.reputation_score * max(len(self.certifications), 1)
        self.reputation_score = (total + new_rating) / (max(len(self.certifications), 1) + 1)


@dataclass
class Project:
    id: UUID = field(default_factory=uuid4)
    client_id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    required_areas: List[ComplianceArea] = field(default_factory=list)
    budget_brl: float = 0.0
    deadline: Optional[datetime] = None
    status: ProjectStatus = ProjectStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)

    def publish(self) -> None:
        if not self.title or not self.required_areas:
            raise ValueError("Projeto precisa de título e áreas de compliance")
        if self.status != ProjectStatus.DRAFT:
            raise ValueError("Apenas projetos em rascunho podem ser publicados")
        self.status = ProjectStatus.OPEN

    def start(self) -> None:
        if self.status != ProjectStatus.OPEN:
            raise ValueError("Projeto precisa estar aberto para iniciar")
        self.status = ProjectStatus.IN_PROGRESS

    def complete(self) -> None:
        if self.status != ProjectStatus.IN_PROGRESS:
            raise ValueError("Projeto precisa estar em andamento para ser concluído")
        self.status = ProjectStatus.COMPLETED


@dataclass
class Proposal:
    id: UUID = field(default_factory=uuid4)
    project_id: UUID = field(default_factory=uuid4)
    freelancer_id: UUID = field(default_factory=uuid4)
    cover_letter: str = ""
    proposed_rate_brl: float = 0.0
    estimated_hours: int = 0
    status: ProposalStatus = ProposalStatus.PENDING
    submitted_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_cost_brl(self) -> float:
        return self.proposed_rate_brl * self.estimated_hours

    def accept(self) -> None:
        if self.status != ProposalStatus.PENDING:
            raise ValueError("Apenas propostas pendentes podem ser aceitas")
        self.status = ProposalStatus.ACCEPTED

    def reject(self) -> None:
        if self.status != ProposalStatus.PENDING:
            raise ValueError("Apenas propostas pendentes podem ser rejeitadas")
        self.status = ProposalStatus.REJECTED


@dataclass
class AuditEvent:
    """
    ADR-003: Audit trail imutável para rastreabilidade regulatória.
    Fitness function garante que eventos de auditoria nunca sejam deletados.
    """

    id: UUID = field(default_factory=uuid4)
    entity_type: str = ""
    entity_id: UUID = field(default_factory=uuid4)
    action: str = ""
    actor_id: UUID = field(default_factory=uuid4)
    payload: dict = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=datetime.utcnow)