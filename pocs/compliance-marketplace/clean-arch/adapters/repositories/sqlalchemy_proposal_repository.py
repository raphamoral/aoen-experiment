from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from entities.proposal import Proposal
from entities.value_objects import Money, ProposalStatus
from frameworks.database.models import ProposalModel
from use_cases.ports import ProposalRepository


class SQLAlchemyProposalRepository(ProposalRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, proposal: Proposal) -> Proposal:
        model = self._session.get(ProposalModel, str(proposal.id))
        if model:
            model.status = proposal.status.value
        else:
            model = self._to_model(proposal)
            self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, proposal_id: UUID) -> Optional[Proposal]:
        model = self._session.get(ProposalModel, str(proposal_id))
        return self._to_entity(model) if model else None

    def find_by_project(self, project_id: UUID) -> List[Proposal]:
        models = (
            self._session.query(ProposalModel)
            .filter(ProposalModel.project_id == str(project_id))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_freelancer(self, freelancer_id: UUID) -> List[Proposal]:
        models = (
            self._session.query(ProposalModel)
            .filter(ProposalModel.freelancer_id == str(freelancer_id))
            .all()
        )
        return [self._to_entity(m) for m in models]

    def reject_all_pending_for_project(self, project_id: UUID, except_id: UUID) -> None:
        (
            self._session.query(ProposalModel)
            .filter(
                ProposalModel.project_id == str(project_id),
                ProposalModel.id != str(except_id),
                ProposalModel.status == ProposalStatus.PENDING.value,
            )
            .update({"status": ProposalStatus.REJECTED.value})
        )
        self._session.commit()

    @staticmethod
    def _to_model(proposal: Proposal) -> ProposalModel:
        return ProposalModel(
            id=str(proposal.id),
            project_id=str(proposal.project_id),
            freelancer_id=str(proposal.freelancer_id),
            proposed_rate_amount=str(proposal.proposed_rate.amount),
            proposed_rate_currency=proposal.proposed_rate.currency,
            cover_letter=proposal.cover_letter,
            estimated_hours=proposal.estimated_hours,
            status=proposal.status.value,
            submitted_at=proposal.submitted_at,
        )

    @staticmethod
    def _to_entity(model: ProposalModel) -> Proposal:
        return Proposal(
            id=UUID(model.id),
            project_id=UUID(model.project_id),
            freelancer_id=UUID(model.freelancer_id),
            proposed_rate=Money(Decimal(model.proposed_rate_amount), model.proposed_rate_currency),
            cover_letter=model.cover_letter,
            estimated_hours=model.estimated_hours,
            status=ProposalStatus(model.status),
            submitted_at=model.submitted_at,
        )