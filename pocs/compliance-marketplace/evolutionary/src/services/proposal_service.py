from uuid import UUID, uuid4

from src.domain.models import AuditEvent, Proposal, ProposalStatus
from src.infrastructure.repositories import (
    AuditRepository,
    FreelancerRepository,
    ProjectRepository,
    ProposalRepository,
)


class ProposalService:
    def __init__(
        self,
        proposal_repo: ProposalRepository,
        project_repo: ProjectRepository,
        freelancer_repo: FreelancerRepository,
        audit: AuditRepository,
    ):
        self.proposal_repo = proposal_repo
        self.project_repo = project_repo
        self.freelancer_repo = freelancer_repo
        self.audit = audit

    async def submit_proposal(
        self,
        project_id: UUID,
        freelancer_id: UUID,
        cover_letter: str,
        proposed_rate_brl: float,
        estimated_hours: int,
    ) -> Proposal:
        project = await self.project_repo.find_by_id(project_id)
        if not project:
            raise ValueError("Projeto não encontrado")

        freelancer = await self.freelancer_repo.find_by_id(freelancer_id)
        if not freelancer:
            raise ValueError("Freelancer não encontrado")

        for area in project.required_areas:
            if not freelancer.is_eligible_for(area):
                raise ValueError(
                    f"Freelancer não possui especialização em {area.value}"
                )

        proposal = Proposal(
            id=uuid4(),
            project_id=project_id,
            freelancer_id=freelancer_id,
            cover_letter=cover_letter,
            proposed_rate_brl=proposed_rate_brl,
            estimated_hours=estimated_hours,
        )
        await self.proposal_repo.save(proposal)
        await self.audit.record(
            AuditEvent(
                entity_type="proposal",
                entity_id=proposal.id,
                action="submitted",
                actor_id=freelancer_id,
                payload={
                    "project_id": str(project_id),
                    "total_cost": proposal.total_cost_brl,
                },
            )
        )
        return proposal

    async def accept_proposal(self, proposal_id: UUID, actor_id: UUID) -> Proposal:
        proposal = await self.proposal_repo.find_by_id(proposal_id)
        if not proposal:
            raise ValueError("Proposta não encontrada")
        proposal.accept()
        await self.proposal_repo.update_status(proposal_id, ProposalStatus.ACCEPTED)
        await self.audit.record(
            AuditEvent(
                entity_type="proposal",
                entity_id=proposal_id,
                action="accepted",
                actor_id=actor_id,
                payload={},
            )
        )
        return proposal

    async def list_for_project(self, project_id: UUID) -> list[Proposal]:
        return await self.proposal_repo.find_by_project(project_id)