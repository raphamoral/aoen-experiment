from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from adapters.output.persistence.models import ContractModel
from domain.entities.contract import Contract, ContractStatus, PaymentStatus
from domain.value_objects.money import Money
from ports.output.contract_repository import IContractRepository


class SQLAlchemyContractRepository(IContractRepository):

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, contract: Contract) -> None:
        self._db.add(self._to_model(contract))
        self._db.commit()

    def find_by_id(self, contract_id: str) -> Optional[Contract]:
        model = self._db.query(ContractModel).filter_by(id=contract_id).first()
        return self._to_entity(model) if model else None

    def find_by_project(self, project_id: str) -> Optional[Contract]:
        model = self._db.query(ContractModel).filter_by(project_id=project_id).first()
        return self._to_entity(model) if model else None

    def find_by_freelancer(self, freelancer_id: str) -> List[Contract]:
        return [
            self._to_entity(m)
            for m in self._db.query(ContractModel).filter_by(freelancer_id=freelancer_id).all()
        ]

    def find_by_client(self, client_id: str) -> List[Contract]:
        return [
            self._to_entity(m)
            for m in self._db.query(ContractModel).filter_by(client_id=client_id).all()
        ]

    def update(self, contract: Contract) -> None:
        model = self._db.query(ContractModel).filter_by(id=contract.id).first()
        if model:
            model.status = contract.status.value
            model.payment_status = contract.payment_status.value
            model.payment_reference = contract.payment_reference
            model.updated_at = contract.updated_at
            self._db.commit()

    def _to_model(self, c: Contract) -> ContractModel:
        return ContractModel(
            id=c.id,
            project_id=c.project_id,
            proposal_id=c.proposal_id,
            freelancer_id=c.freelancer_id,
            client_id=c.client_id,
            agreed_daily_rate_amount=c.agreed_daily_rate.amount,
            agreed_daily_rate_currency=c.agreed_daily_rate.currency,
            total_days=c.total_days,
            start_date=c.start_date,
            end_date=c.end_date,
            status=c.status.value,
            payment_status=c.payment_status.value,
            payment_reference=c.payment_reference,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )

    def _to_entity(self, m: ContractModel) -> Contract:
        return Contract(
            id=m.id,
            project_id=m.project_id,
            proposal_id=m.proposal_id,
            freelancer_id=m.freelancer_id,
            client_id=m.client_id,
            agreed_daily_rate=Money(
                Decimal(str(m.agreed_daily_rate_amount)), m.agreed_daily_rate_currency
            ),
            total_days=m.total_days,
            start_date=m.start_date,
            end_date=m.end_date,
            status=ContractStatus(m.status),
            payment_status=PaymentStatus(m.payment_status),
            payment_reference=m.payment_reference,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )