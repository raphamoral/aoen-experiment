from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from entities.client import Client
from entities.value_objects import Email
from frameworks.database.models import ClientModel
from use_cases.ports import ClientRepository


class SQLAlchemyClientRepository(ClientRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, client: Client) -> Client:
        model = self._session.get(ClientModel, str(client.id))
        if model:
            self._update_model(model, client)
        else:
            model = self._to_model(client)
            self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, client_id: UUID) -> Optional[Client]:
        model = self._session.get(ClientModel, str(client_id))
        return self._to_entity(model) if model else None

    def find_by_email(self, email: str) -> Optional[Client]:
        model = (
            self._session.query(ClientModel)
            .filter(ClientModel.email == email.lower())
            .first()
        )
        return self._to_entity(model) if model else None

    @staticmethod
    def _to_model(client: Client) -> ClientModel:
        return ClientModel(
            id=str(client.id),
            company_name=client.company_name,
            email=client.email.value,
            cnpj=client.cnpj,
            industry=client.industry,
            contact_name=client.contact_name,
        )

    @staticmethod
    def _update_model(model: ClientModel, client: Client) -> None:
        model.company_name = client.company_name
        model.industry = client.industry
        model.contact_name = client.contact_name

    @staticmethod
    def _to_entity(model: ClientModel) -> Client:
        return Client(
            id=UUID(model.id),
            company_name=model.company_name,
            email=Email(model.email),
            cnpj=model.cnpj,
            industry=model.industry,
            contact_name=model.contact_name,
        )