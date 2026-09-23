"""
Repositórios: única camada que conhece ORM/SQL.

ADR-005: Repository pattern como seam de evolução.
Se migrarmos para Event Sourcing ou NoSQL, apenas esta camada muda.
"""

import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import (
    AuditEvent,
    Certification,
    ComplianceArea,
    Freelancer,
    Proposal,
    ProposalStatus,
    Project,
    ProjectStatus,
)
from src.infrastructure.orm_models import (
    AuditEventORM,
    FreelancerORM,
    ProposalORM,
    ProjectORM,
)


def _orm_to_freelancer(row: FreelancerORM) -> Freelancer:
    areas = [ComplianceArea(a) for a in json.loads(row.areas_json)]
    certs_raw = json.loads(row.certifications_json)
    certs = [
        Certification(
            name=c["name"],
            issuer=c["issuer"],
            issued_at=datetime.fromisoformat(c["issued_at"]),
            expires_at=datetime.fromisoformat(c["expires_at"]) if c.get("expires_at") else None,
            verified=c.get("verified", False),
        )
        for c in certs_raw
    ]
    return Freelancer(
        id=UUID(row.id),
        name=row.name,
        email=row.email,
        bio=row.bio,
        areas=areas,
        certifications=certs,
        hourly_rate_brl=row.hourly_rate_brl,
        reputation_score=row.reputation_score,
        created_at=row.created_at,
    )


def _orm_to_project(row: ProjectORM) -> Project:
    areas = [ComplianceArea(a) for a in json.loads(row.required_areas_json)]
    return Project(
        id=UUID(row.id),
        client_id=UUID(row.client_id),
        title=row.title,
        description=row.description,
        required_areas=areas,
        budget_brl=row.budget_brl,
        deadline=row.deadline,
        status=ProjectStatus(row.status),
        created_at=row.created_at,
    )


def _orm_to_proposal(row: ProposalORM) -> Proposal:
    return Proposal(
        id=UUID(row.id),
        project_id=UUID(row.project_id),
        freelancer_id=UUID(row.freelancer_id),
        cover_letter=row.cover_letter,
        proposed_rate_brl=row.proposed_rate_brl,
        estimated_hours=row.estimated_hours,
        status=ProposalStatus(row.status),
        submitted_at=row.submitted_at,
    )


class FreelancerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, freelancer: Freelancer) -> Freelancer:
        certs_serializable = [
            {
                "name": c.name,
                "issuer": c.issuer,
                "issued_at": c.issued_at.isoformat(),
                "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                "verified": c.verified,
            }
            for c in freelancer.certifications
        ]
        orm = FreelancerORM(
            id=str(freelancer.id),
            name=freelancer.name,
            email=freelancer.email,
            bio=freelancer.bio,
            areas_json=json.dumps([a.value for a in freelancer.areas]),
            certifications_json=json.dumps(certs_serializable),
            hourly_rate_brl=freelancer.hourly_rate_brl,
            reputation_score=freelancer.reputation_score,
            created_at=freelancer.created_at,
        )
        self.db.add(orm)
        return freelancer

    async def find_by_id(self, freelancer_id: UUID) -> Optional[Freelancer]:
        result = await self.db.execute(
            select(FreelancerORM).where(FreelancerORM.id == str(freelancer_id))
        )
        row = result.scalar_one_or_none()
        return _orm_to_freelancer(row) if row else None

    async def find_by_area(self, area: ComplianceArea) -> List[Freelancer]:
        result = await self.db.execute(select(FreelancerORM))
        rows = result.scalars().all()
        freelancers = [_orm_to_freelancer(r) for r in rows]
        return [f for f in freelancers if f.is_eligible_for(area)]

    async def list_all(self) -> List[Freelancer]:
        result = await self.db.execute(select(FreelancerORM))
        return [_orm_to_freelancer(r) for r in result.scalars().all()]


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, project: Project) -> Project:
        orm = ProjectORM(
            id=str(project.id),
            client_id=str(project.client_id),
            title=project.title,
            description=project.description,
            required_areas_json=json.dumps([a.value for a in project.required_areas]),
            budget_brl=project.budget_brl,
            deadline=project.deadline,
            status=project.status.value,
            created_at=project.created_at,
        )
        self.db.add(orm)
        return project

    async def find_by_id(self, project_id: UUID) -> Optional[Project]:
        result = await self.db.execute(
            select(ProjectORM).where(ProjectORM.id == str(project_id))
        )
        row = result.scalar_one_or_none()
        return _orm_to_project(row) if row else None

    async def list_open(self) -> List[Project]:
        result = await self.db.execute(
            select(ProjectORM).where(ProjectORM.status == "open")
        )
        return [_orm_to_project(r) for r in result.scalars().all()]

    async def update_status(self, project_id: UUID, status: ProjectStatus) -> None:
        result = await self.db.execute(
            select(ProjectORM).where(ProjectORM.id == str(project_id))
        )
        row = result.scalar_one_or_none()
        if row:
            row.status = status.value


class ProposalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, proposal: Proposal) -> Proposal:
        orm = ProposalORM(
            id=str(proposal.id),
            project_id=str(proposal.project_id),
            freelancer_id=str(proposal.freelancer_id),
            cover_letter=proposal.cover_letter,
            proposed_rate_brl=proposal.proposed_rate_brl,
            estimated_hours=proposal.estimated_hours,
            status=proposal.status.value,
            submitted_at=proposal.submitted_at,
        )
        self.db.add(orm)
        return proposal

    async def find_by_project(self, project_id: UUID) -> List[Proposal]:
        result = await self.db.execute(
            select(ProposalORM).where(ProposalORM.project_id == str(project_id))
        )
        return [_orm_to_proposal(r) for r in result.scalars().all()]

    async def find_by_id(self, proposal_id: UUID) -> Optional[Proposal]:
        result = await self.db.execute(
            select(ProposalORM).where(ProposalORM.id == str(proposal_id))
        )
        row = result.scalar_one_or_none()
        return _orm_to_proposal(row) if row else None

    async def update_status(self, proposal_id: UUID, status: ProposalStatus) -> None:
        result = await self.db.execute(
            select(ProposalORM).where(ProposalORM.id == str(proposal_id))
        )
        row = result.scalar_one_or_none()
        if row:
            row.status = status.value


class AuditRepository:
    """Audit trail append-only — fitness function verifica ausência de DELETE."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record(self, event: AuditEvent) -> None:
        orm = AuditEventORM(
            id=str(event.id),
            entity_type=event.entity_type,
            entity_id=str(event.entity_id),
            action=event.action,
            actor_id=str(event.actor_id),
            payload_json=json.dumps(event.payload),
            occurred_at=event.occurred_at,
        )
        self.db.add(orm)

    async def find_by_entity(self, entity_type: str, entity_id: UUID) -> List[AuditEvent]:
        result = await self.db.execute(
            select(AuditEventORM)
            .where(AuditEventORM.entity_type == entity_type)
            .where(AuditEventORM.entity_id == str(entity_id))
            .order_by(AuditEventORM.occurred_at)
        )
        rows = result.scalars().all()
        return [
            AuditEvent(
                id=UUID(r.id),
                entity_type=r.entity_type,
                entity_id=UUID(r.entity_id),
                action=r.action,
                actor_id=UUID(r.actor_id),
                payload=json.loads(r.payload_json),
                occurred_at=r.occurred_at,
            )
            for r in rows
        ]