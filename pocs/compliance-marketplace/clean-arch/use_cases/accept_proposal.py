from dataclasses import dataclass
from uuid import UUID

from entities.contract import Contract
from use_cases.ports import ClientRepository, ContractRepository, ProjectRepository, ProposalRepository


@dataclass
class AcceptProposalInput:
    proposal_id: str
    client_id: str


@dataclass
class AcceptProposalOutput:
    contract: Contract


class AcceptProposalUseCase:
    def __init__(
        self,
        proposal_repo: ProposalRepository,
        project_repo: ProjectRepository,
        client_repo: ClientRepository,
        contract_repo: ContractRepository,
    ) -> None:
        self._proposal_repo = proposal_repo
        self._project_repo = project_repo
        self._client_repo = client_repo
        self._contract_repo = contract_repo

    def execute(self, input_data: AcceptProposalInput) -> AcceptProposalOutput:
        proposal_id = UUID(input_data.proposal_id)
        client_id = UUID(input_data.client_id)

        proposal = self._proposal_repo.find_by_id(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {input_data.proposal_id}")

        project = self._project_repo.find_by_id(proposal.project_id)
        if not project:
            raise ValueError("Associated project not found")
        if str(project.client_id) != input_data.client_id:
            raise ValueError("Only the project owner can accept proposals")

        proposal.accept()
        self._proposal_repo.save(proposal)

        self._proposal_repo.reject_all_pending_for_project(
            project_id=project.id,
            except_id=proposal_id,
        )

        project.start()
        self._project_repo.save(project)

        contract = Contract.from_proposal(proposal=proposal, client_id=client_id)
        saved_contract = self._contract_repo.save(contract)
        return AcceptProposalOutput(contract=saved_contract)