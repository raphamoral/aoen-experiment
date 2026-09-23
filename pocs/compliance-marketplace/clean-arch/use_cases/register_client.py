from dataclasses import dataclass

from entities.client import Client
from use_cases.ports import ClientRepository


@dataclass
class RegisterClientInput:
    company_name: str
    email: str
    cnpj: str
    industry: str
    contact_name: str


@dataclass
class RegisterClientOutput:
    client: Client


class RegisterClientUseCase:
    def __init__(self, client_repo: ClientRepository) -> None:
        self._repo = client_repo

    def execute(self, input_data: RegisterClientInput) -> RegisterClientOutput:
        existing = self._repo.find_by_email(input_data.email)
        if existing:
            raise ValueError(f"Email already registered: {input_data.email}")

        client = Client.create(
            company_name=input_data.company_name,
            email=input_data.email,
            cnpj=input_data.cnpj,
            industry=input_data.industry,
            contact_name=input_data.contact_name,
        )
        saved = self._repo.save(client)
        return RegisterClientOutput(client=saved)