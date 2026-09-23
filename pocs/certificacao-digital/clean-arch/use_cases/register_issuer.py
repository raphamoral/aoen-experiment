from dataclasses import dataclass

from entities.issuer import Issuer
from use_cases.ports.issuer_repository import IssuerRepository


@dataclass
class RegisterIssuerInput:
    name: str
    document: str


@dataclass
class RegisterIssuerOutput:
    issuer: Issuer


class RegisterIssuerUseCase:
    def __init__(self, issuer_repo: IssuerRepository) -> None:
        self._issuer_repo = issuer_repo

    def execute(self, data: RegisterIssuerInput) -> RegisterIssuerOutput:
        # Entity validates and normalises document in __post_init__
        issuer = Issuer(name=data.name, document=data.document)

        existing = self._issuer_repo.find_by_document(issuer.document)
        if existing:
            raise ValueError(f"Document '{data.document}' is already registered")

        saved = self._issuer_repo.save(issuer)
        return RegisterIssuerOutput(issuer=saved)