from typing import List

from entities.proposal import Proposal
from entities.contract import Contract
from use_cases.proposal.submit_proposal import SubmitProposal, SubmitProposalInput
from use_cases.proposal.accept_proposal import AcceptProposal
from use_cases.proposal.list_proposals import ListProposalsByProject
from use_cases.contract.get_contract import GetContract
from adapters.presenters.schemas import (
    ProposalCreateRequest,
    ProposalAcceptRequest,
    ProposalResponse,
    ContractResponse,
)


class ProposalController:
    def __init__(
        self,
        submit_uc: SubmitProposal,
        accept_uc: AcceptProposal,
        list_uc: ListProposalsByProject,
        get_contract_uc: GetContract,
    ):
        self.submit_uc = submit_uc
        self.accept_uc = accept_uc
        self.list_uc = list_uc
        self.get_contract_uc = get_contract_uc

    def submit(self, request: ProposalCreateRequest) -> ProposalResponse:
        proposal = self.submit_uc.execute(
            SubmitProposalInput(
                project_id=request.project_id,
                freelancer_id=request.freelancer_id,
                price=request.price,
                cover_letter=request.cover_letter,
                estimated_days=request.estimated_days,
            )
        )
        return self._proposal_to_response(proposal)

    def accept(self, proposal_id: str, request: ProposalAcceptRequest) -> ContractResponse:
        contract = self.accept_uc.execute(proposal_id, request.client_id)
        return self._contract_to_response(contract)

    def list_by_project(self, project_id: str, client_id: str) -> List[ProposalResponse]:
        return [
            self._proposal_to_response(p)
            for p in self.list_uc.execute(project_id, client_id)
        ]

    def _proposal_to_response(self, p: Proposal) -> ProposalResponse:
        return ProposalResponse(
            id=p.id,
            project_id=p.project_id,
            freelancer_id=p.freelancer_id,
            price=p.price,
            cover_letter=p.cover_letter,
            estimated_days=p.estimated_days,
            status=p.status.value,
            submitted_at=p.submitted_at,
        )

    def _contract_to_response(self, c: Contract) -> ContractResponse:
        return ContractResponse(
            id=c.id,
            project_id=c.project_id,
            proposal_id=c.proposal_id,
            freelancer_id=c.freelancer_id,
            client_id=c.client_id,
            agreed_price=c.agreed_price,
            estimated_days=c.estimated_days,
            status=c.status.value,
            created_at=c.created_at,
            completed_at=c.completed_at,
        )