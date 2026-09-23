from typing import List

from domain.entities.proposal import Proposal, ProposalStatus


class ProposalDomainService:
    """
    Serviço de Domínio: regras de negócio para o ciclo de vida de propostas.

    Quando uma proposta é aceita, todas as concorrentes para o mesmo projeto
    devem ser automaticamente rejeitadas (invariante de negócio).
    """

    def reject_competing_proposals(
        self, accepted: Proposal, all_project_proposals: List[Proposal]
    ) -> List[Proposal]:
        rejected = []
        for proposal in all_project_proposals:
            if (
                proposal.id != accepted.id
                and proposal.project_id == accepted.project_id
                and proposal.status == ProposalStatus.PENDING
            ):
                proposal.reject()
                rejected.append(proposal)
        return rejected