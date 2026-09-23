from entities.contract import Contract
from entities.proposal import ProposalStatus
from entities.project import ProjectStatus
from use_cases.ports.repositories import (
    ProposalRepository,
    ProjectRepository,
    ContractRepository,
    ClientRepository,
)


class AcceptProposal:
    def __init__(
        self,
        proposal_repo: ProposalRepository,
        project_repo: ProjectRepository,
        contract_repo: ContractRepository,
        client_repo: ClientRepository,
    ):
        self.proposal_repo = proposal_repo
        self.project_repo = project_repo
        self.contract_repo = contract_repo
        self.client_repo = client_repo

    def execute(self, proposal_id: str, client_id: str) -> Contract:
        proposal = self.proposal_repo.find_by_id(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal '{proposal_id}' not found")
        if proposal.status != ProposalStatus.PENDING:
            raise ValueError(f"Proposal is not pending (current status: '{proposal.status}')")

        project = self.project_repo.find_by_id(proposal.project_id)
        if not project:
            raise ValueError(f"Project '{proposal.project_id}' not found")
        if project.client_id != client_id:
            raise ValueError("Only the project owner can accept proposals")
        if project.status != ProjectStatus.OPEN:
            raise ValueError("Project is no longer accepting proposals")

        # Reject all other pending proposals for this project
        for p in self.proposal_repo.find_by_project(project.id):
            if p.id != proposal_id and p.status == ProposalStatus.PENDING:
                p.reject()
                self.proposal_repo.update(p)

        proposal.accept()
        self.proposal_repo.update(proposal)

        project.start()
        self.project_repo.update(project)

        contract = Contract(
            project_id=project.id,
            proposal_id=proposal.id,
            freelancer_id=proposal.freelancer_id,
            client_id=client_id,
            agreed_price=proposal.price,
            estimated_days=proposal.estimated_days,
        )
        return self.contract_repo.save(contract)