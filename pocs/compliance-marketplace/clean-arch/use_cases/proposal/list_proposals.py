from typing import List

from entities.proposal import Proposal
from use_cases.ports.repositories import ProposalRepository, ProjectRepository


class ListProposalsByProject:
    def __init__(self, proposal_repo: ProposalRepository, project_repo: ProjectRepository):
        self.proposal_repo = proposal_repo
        self.project_repo = project_repo

    def execute(self, project_id: str, client_id: str) -> List[Proposal]:
        project = self.project_repo.find_by_id(project_id)
        if not project:
            raise ValueError(f"Project '{project_id}' not found")
        if project.client_id != client_id:
            raise ValueError("Only the project owner can view proposals")
        return self.proposal_repo.find_by_project(project_id)