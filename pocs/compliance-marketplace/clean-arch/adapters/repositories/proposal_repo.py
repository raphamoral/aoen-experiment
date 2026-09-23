from typing import List, Optional
from sqlalchemy.orm import Session

from entities.proposal import Proposal, ProposalStatus
from use_cases.ports.repositories import ProposalRepository
from adapters.repositories.orm_models import ProposalModel


class SQLAlchemyProposalRepository(ProposalRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, proposal: Proposal) -> Proposal:
        model = ProposalModel(
            id=proposal.id,
            project_id=proposal.project_id,
            freelancer_id=proposal.freelancer_id,
            price=proposal.price,
            cover_letter=proposal.cover_letter,
            estimated_days=proposal.estimated_days,
            status=proposal.status.value,
            submitted_at=proposal.submitted_at,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, id: str) -> Optional[Proposal]:
        model = self.session.query(ProposalModel).filter_by(id=id).first()
        return self._to_entity(model) if model else None

    def find_by_project(self, project_id: str) -> List[Proposal]:
        models = self.session.query(ProposalModel).filter_by(project_id=project_id).all()
        return [self._to_entity(m) for m in models]

    def find_by_freelancer(self, freelancer_id: str) -> List[Proposal]:
        models = self.session.query(ProposalModel).filter_by(freelancer_id=freelancer_id).all()
        return [self._to_entity(m) for m in models]

    def find_by_project_and_freelancer(
        self, project_id: str, freelancer_id: str
    ) -> Optional[Proposal]:
        model = (
            self.session.query(ProposalModel)
            .filter_by(project_id=project_id, freelancer_id=freelancer_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def update(self, proposal: Proposal) -> Proposal:
        model = self.session.query(ProposalModel).filter_by(id=proposal.id).first()
        if not model:
            raise ValueError(f"Proposal '{proposal.id}' not found for update")
        model.status = proposal.status.value
        model.price = proposal.price
        model.cover_letter = proposal.cover_letter
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def _to_entity(self, model: ProposalModel) -> Proposal:
        return Proposal(
            id=model.id,
            project_id=model.project_id,
            freelancer_id=model.freelancer_id,
            price=model.price,
            cover_letter=model.cover_letter,
            estimated_days=model.estimated_days,
            status=ProposalStatus(model.status),
            submitted_at=model.submitted_at,
        )