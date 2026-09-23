from decimal import Decimal
from typing import List
from uuid import UUID

from domain.entities.proposal import Proposal
from domain.exceptions import (
    FreelancerNotFound,
    ProjectNotFound,
    ProposalNotFound,
)
from domain.services.matching_service import FreelancerMatchingService
from domain.services.proposal_service import ProposalDomainService
from ports.inbound.proposal_use_case import IProposalUseCase
from ports.outbound.freelancer_repository import IFreelancerRepository
from ports.outbound.notification_service import INotificationService
from ports.outbound.project_repository import IProjectRepository
from ports.outbound.proposal_repository import IProposalRepository


class ProposalApplicationService(IProposalUseCase):
    """
    Serviço de Aplicação: implementa a porta de entrada IProposalUseCase.
    Orquestra o ciclo de vida de propostas, notificações e atribuição de projeto.
    """

    def __init__(
        self,
        proposal_repo: IProposalRepository,
        project_repo: IProjectRepository,
        freelancer_repo: IFreelancerRepository,
        notification_service: INotificationService,
        matching_service: FreelancerMatchingService,
        proposal_domain_service: ProposalDomainService,
    ) -> None:
        self._proposal_repo = proposal_repo
        self._project_repo = project_repo
        self._freelancer_repo = freelancer_repo
        self._notification = notification_service
        self._matching = matching_service
        self._proposal_svc = proposal_domain_service

    def submit_proposal(
        self,
        project_id: UUID,
        freelancer_id: UUID,
        proposed_rate: Decimal,
        cover_letter: str,
        estimated_hours: int,
    ) -> Proposal:
        project = self._project_repo.find_by_id(project_id)
        if not project:
            raise ProjectNotFound(project_id)

        freelancer = self._freelancer_repo.find_by_id(freelancer_id)
        if not freelancer:
            raise FreelancerNotFound(freelancer_id)

        # Regra de domínio: freelancer deve ser elegível
        self._matching.assert_eligible(freelancer, project)

        proposal = Proposal(
            project_id=project_id,
            freelancer_id=freelancer_id,
            proposed_rate=proposed_rate,
            cover_letter=cover_letter,
            estimated_hours=estimated_hours,
        )
        saved = self._proposal_repo.save(proposal)

        # Porta de saída: notificação
        self._notification.notify_proposal_received(
            client_email=f"cliente-{project.client_id}@marketplace.com",
            project_title=project.title,
            freelancer_name=freelancer.name,
        )
        return saved

    def accept_proposal(self, proposal_id: UUID) -> Proposal:
        proposal = self._get_or_raise(proposal_id)
        proposal.accept()
        self._proposal_repo.save(proposal)

        # Atribui freelancer ao projeto
        project = self._project_repo.find_by_id(proposal.project_id)
        if project:
            project.assign_freelancer(proposal.freelancer_id)
            self._project_repo.save(project)

        # Rejeita propostas concorrentes (invariante de domínio)
        all_proposals = self._proposal_repo.find_by_project(proposal.project_id)
        for competing in self._proposal_svc.reject_competing_proposals(proposal, all_proposals):
            self._proposal_repo.save(competing)

        # Notifica freelancer vencedor
        freelancer = self._freelancer_repo.find_by_id(proposal.freelancer_id)
        if freelancer and project:
            self._notification.notify_proposal_accepted(
                freelancer_email=freelancer.email,
                project_title=project.title,
            )
        return proposal

    def reject_proposal(self, proposal_id: UUID) -> Proposal:
        proposal = self._get_or_raise(proposal_id)
        proposal.reject()
        self._proposal_repo.save(proposal)

        freelancer = self._freelancer_repo.find_by_id(proposal.freelancer_id)
        project = self._project_repo.find_by_id(proposal.project_id)
        if freelancer and project:
            self._notification.notify_proposal_rejected(
                freelancer_email=freelancer.email,
                project_title=project.title,
            )
        return proposal

    def withdraw_proposal(self, proposal_id: UUID) -> Proposal:
        proposal = self._get_or_raise(proposal_id)
        proposal.withdraw()
        return self._proposal_repo.save(proposal)

    def list_proposals_for_project(self, project_id: UUID) -> List[Proposal]:
        return self._proposal_repo.find_by_project(project_id)

    def list_proposals_by_freelancer(self, freelancer_id: UUID) -> List[Proposal]:
        return self._proposal_repo.find_by_freelancer(freelancer_id)

    def _get_or_raise(self, proposal_id: UUID) -> Proposal:
        proposal = self._proposal_repo.find_by_id(proposal_id)
        if not proposal:
            raise ProposalNotFound(proposal_id)
        return proposal