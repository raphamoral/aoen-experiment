from typing import List, Optional
from sqlalchemy.orm import Session

from entities.contract import Contract, ContractStatus
from use_cases.ports.repositories import ContractRepository
from adapters.repositories.orm_models import ContractModel


class SQLAlchemyContractRepository(ContractRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, contract: Contract) -> Contract:
        model = ContractModel(
            id=contract.id,
            project_id=contract.project_id,
            proposal_id=contract.proposal_id,
            freelancer_id=contract.freelancer_id,
            client_id=contract.client_id,
            agreed_price=contract.agreed_price,
            estimated_days=contract.estimated_days,
            status=contract.status.value,
            created_at=contract.created_at,
            completed_at=contract.completed_at,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, id: str) -> Optional[Contract]:
        model = self.session.query(ContractModel).filter_by(id=id).first()
        return self._to_entity(model) if model else None

    def find_by_project(self, project_id: str) -> Optional[Contract]:
        model = self.session.query(ContractModel).filter_by(project_id=project_id).first()
        return self._to_entity(model) if model else None

    def find_by_freelancer(self, freelancer_id: str) -> List[Contract]:
        models = self.session.query(ContractModel).filter_by(freelancer_id=freelancer_id).all()
        return [self._to_entity(m) for m in models]

    def update(self, contract: Contract) -> Contract:
        model = self.session.query(ContractModel).filter_by(id=contract.id).first()
        if not model:
            raise ValueError(f"Contract '{contract.id}' not found for update")
        model.status = contract.status.value
        model.completed_at = contract.completed_at
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def _to_entity(self, model: ContractModel) -> Contract:
        return Contract(
            id=model.id,
            project_id=model.project_id,
            proposal_id=model.proposal_id,
            freelancer_id=model.freelancer_id,
            client_id=model.client_id,
            agreed_price=model.agreed_price,
            estimated_days=model.estimated_days,
            status=ContractStatus(model.status),
            created_at=model.created_at,
            completed_at=model.completed_at,
        )