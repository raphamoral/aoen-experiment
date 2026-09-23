from typing import Optional
from sqlalchemy.orm import Session

from entities.client import Client
from use_cases.ports.repositories import ClientRepository
from adapters.repositories.orm_models import ClientModel


class SQLAlchemyClientRepository(ClientRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, client: Client) -> Client:
        model = ClientModel(
            id=client.id,
            name=client.name,
            email=client.email,
            company=client.company,
            industry=client.industry,
            is_active=client.is_active,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, id: str) -> Optional[Client]:
        model = self.session.query(ClientModel).filter_by(id=id).first()
        return self._to_entity(model) if model else None

    def find_by_email(self, email: str) -> Optional[Client]:
        model = self.session.query(ClientModel).filter_by(email=email).first()
        return self._to_entity(model) if model else None

    def _to_entity(self, model: ClientModel) -> Client:
        return Client(
            id=model.id,
            name=model.name,
            email=model.email,
            company=model.company,
            industry=model.industry,
            is_active=model.is_active,
        )