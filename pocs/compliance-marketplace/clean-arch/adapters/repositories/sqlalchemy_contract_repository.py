from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from entities.contract import Contract
from entities.value_objects import Money
from frameworks.database.models import ContractModel
from use_cases.ports import ContractRepository


class SQLAlchemyContractRepository(ContractRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, contract: Contract) -> Contract:
        model = self._session.get(ContractModel, str(contract.id))
        if model:
            model.is_active = contract.is_active
        else:
            model = self._to_model(contract)
            self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_project(self, project_id: UUID) -> Optional[Contract]:
        model = (
            self._session.query(ContractModel)
            .filter(ContractModel.project_id == str(project_id))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_freelancer(self, freelancer_id: UUID) -> List[Contract]:
        models = (
            self._session.query(ContractModel)
            .filter(ContractModel.freelancer_id == str(freelancer_id))
            .all()
        )
        return [self._to_entity(m) for m in models]

    @staticmethod
    def _to_model(contract: Contract) -> ContractModel:
        return ContractModel(
            id=str(contract.id),
            project_id=str(contract.project_id),
            freelancer_id=str(contract.freelancer_id),
            client_id=str(contract.client_id),
            proposal_id=str(contract.proposal_id),
            agreed_rate_amount=str(contract.agreed_rate.amount),
            agreed_rate_currency=contract.agreed_rate.currency,
            estimated_hours=contract.estimated_hours,
            total_value_amount=str(contract.total_value.amount),
            total_value_currency=contract.total_value.currency,
            signed_at=contract.signed_at,
            is_active=contract.is_active,
        )

    @staticmethod
    def _to_entity(model: ContractModel) -> Contract:
        return Contract(
            id=UUID(model.id),
            project_id=UUID(model.project_id),
            freelancer_id=UUID(model.freelancer_id),
            client_id=UUID(model.client_id),
            proposal_id=UUID(model.proposal_id),
            agreed_rate=Money(Decimal(model.agreed_rate_amount), model.agreed_rate_currency),
            estimated_hours=model.estimated_hours,
            total_value=Money(Decimal(model.total_value_amount), model.total_value_currency),
            signed_at=model.signed_at,
            is_active=model.is_active,
        )