from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from adapters.output.persistence.models import ProposalModel
from domain.entities.proposal import Proposal, ProposalStatus
from domain.value_objects.money import Money
from ports.output.proposal_repository import IProposalRepository


class SQLAlchemyProposalRepository(IProposalRepository):

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, proposal: Proposal) -> None:
        self._db.add(self._to_model(proposal))
        self._db.commit()

    def find_by_id(self, proposal_id: str) -> Optional[Proposal]:
        model = self._db.query(ProposalModel).filter_by(id=proposal_id).first()
        return self._to_entity(model) if model else None

    def find_by_project(self, project_id: str) -> List[Proposal]:
        return [
            self._to_entity(m)
            for m in self._db.query(ProposalModel).filter_by(project_id=project_id).all()
        ]

    def find_by_freelancer(self, freelancer_id: str) -> List[Proposal]:
        return [
            self._to_entity(m)
            for m in self._db.query(ProposalModel).filter_by(freelancer_id=freelancer_id).all()
        ]

    def find_by_project_and_freelancer(
        self, project_id: str, freelancer_id: str
    ) -> Optional[Proposal]:
        model = (
            self._db.query(ProposalModel)
            .filter_by(project_id=project_id, freelancer_id=freelancer_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def update(self, proposal: Proposal) -> None:
        model = self._db.query(ProposalModel).filter_by(id=proposal.id).first()
        if model:
            model.proposed_rate_amount = proposal.proposed_rate.amount
            model.proposed_rate_currency = proposal.proposed_rate.currency
            model.cover_letter = proposal.cover_letter
            model.estimated_days = proposal.estimated_days
            model.status = proposal.status.value
            model.updated_at = proposal.updated_at
            self._db.commit()

    def _to_model(self, p: Proposal) -> ProposalModel:
        return ProposalModel(
            id=p.id,
            project_id=p.project_id,
            freelancer_id=p.freelancer_id,
            proposed_rate_amount=p.proposed_rate.amount,
            proposed_rate_currency=p.proposed_rate.currency,
            cover_letter=p.cover_letter,
            estimated_days=p.estimated_days,
            status=p.status.value,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )

    def _to_entity(self, m: ProposalModel) -> Proposal:
        return Proposal(
            id=m.id,
            project_id=m.project_id,
            freelancer_id=m.freelancer_id,
            proposed_rate=Money(
                Decimal(str(m.proposed_rate_amount)), m.proposed_rate_currency
            ),
            cover_letter=m.cover_letter,
            estimated_days=m.estimated_days,
            status=ProposalStatus(m.status),
            created_at=m.created_at,
            updated_at=m.updated_at,
        )