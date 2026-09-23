from dataclasses import dataclass
from uuid import UUID

from entities.proposal import Proposal
from entities.value_objects import ProjectStatus
from use_cases.ports import FreelancerRepository, ProjectRepository, ProposalRepository


@dataclass
class SubmitProposalInput:
    project_id: str
    freelancer_id: str
    proposed_rate_amount: str
    cover_letter: str
    estimated_hours: int


@dataclass
class SubmitProposalOutput:
    proposal: Proposal


class SubmitProposalUseCase:
    def __init__(
        self,
        proposal_repo: ProposalRepository,
        project_repo: ProjectRepository,
        freelancer_repo: FreelancerRepository,
    ) -> None:
        self._proposal_repo = proposal_repo
        self._project_repo = project_repo
        self._freelancer_repo = freelancer_repo

    def execute(self, input_data: SubmitProposalInput) -> SubmitProposalOutput:
        project_id = UUID(input_data.project_id)
        freelancer_id = UUID(input_data.freelancer_id)

        project = self._project_repo.find_by_id(project_id)
        if not project:
            raise ValueError(f"Project not found: {input_data.project_id}")
        if project.status != ProjectStatus.OPEN:
            raise ValueError("Project is not accepting proposals")

        freelancer = self._freelancer_repo.find_by_id(freelancer_id)
        if not freelancer:
            raise ValueError(f"Freelancer not found: {input_data.freelancer_id}")
        if not freelancer.is_available:
            raise ValueError("Freelancer is not available")

        existing = self._proposal_repo.find_by_freelancer(freelancer_id)
        if any(str(p.project_id) == input_data.project_id for p in existing):
            raise ValueError("Freelancer already submitted a proposal for this project")

        proposal = Proposal.create(
            project_id=project_id,
            freelancer_id=freelancer_id,
            proposed_rate_amount=input_data.proposed_rate_amount,
            cover_letter=input_data.cover_letter,
            estimated_hours=input_data.estimated_hours,
        )
        saved = self._proposal_repo.save(proposal)
        return SubmitProposalOutput(proposal=saved)