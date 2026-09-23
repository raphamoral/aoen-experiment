from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from entities.issuer import Issuer
from frameworks.db.models import IssuerModel
from use_cases.ports.issuer_repository import IssuerRepository


class SQLAlchemyIssuerRepository(IssuerRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, issuer: Issuer) -> Issuer:
        model = IssuerModel(
            id=str(issuer.id),
            name=issuer.name,
            document=issuer.document,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, issuer_id: UUID) -> Optional[Issuer]:
        model = self._session.query(IssuerModel).filter_by(id=str(issuer_id)).first()
        return self._to_entity(model) if model else None

    def find_by_document(self, document: str) -> Optional[Issuer]:
        model = self._session.query(IssuerModel).filter_by(document=document).first()
        return self._to_entity(model) if model else None

    @staticmethod
    def _to_entity(model: IssuerModel) -> Issuer:
        # document stored as normalised digits — passes entity validation
        return Issuer(id=UUID(model.id), name=model.name, document=model.document)