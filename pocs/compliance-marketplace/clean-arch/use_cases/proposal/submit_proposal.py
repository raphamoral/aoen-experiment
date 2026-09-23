from dataclasses import dataclass

from entities.proposal import Proposal
from entities.project import ProjectStatus
from use_cases.ports.repositories import (
    ProposalRepository,
    ProjectRepository,
    FreelancerRepository,
)


@dataclass
class SubmitProposalInput:
    project_id: str
    freelancer_id: str
    price: float
    cover_letter: str
    estimated_days: int


class SubmitProposal:
    def __init__(
        self,
        proposal_repo: ProposalRepository,
        project_repo: ProjectRepository,
        freelancer_repo: FreelancerRepository,
    ):
        self.proposal_repo = proposal_repo
        self.project_repo = project_repo
        self.freelancer_repo = freelancer_repo

    def execute(self, input: SubmitProposalInput) -> Proposal:
        project = self.project_repo.find_by_id(input.project_id)
        if not project:
            raise ValueError(f"Project '{input.project_id}' not found")
        if project.status != ProjectStatus.OPEN:
            raise ValueError("Proposals can only be submitted for open projects")

        freelancer = self.freelancer_repo.find_by_id(input.freelancer_id)
        if not freelancer:
            raise ValueError(f"Freelancer '{input.freelancer_id}' not found")
        if not freelancer.is_active:
            raise ValueError("Inactive freelancers cannot submit proposals")

        if self.proposal_repo.find_by_project_and_freelancer(
            input.project_id, input.freelancer_id
        ):
            raise ValueError("A proposal for this project was already submitted by this freelancer")

        proposal = Proposal(
            project_id=input.project_id,
            freelancer_id=input.freelancer_id,
            price=input.price,
            cover_letter=input.cover_letter,
            estimated_days=input.estimated_days,
        )
        return self.proposal_repo.save(proposal)