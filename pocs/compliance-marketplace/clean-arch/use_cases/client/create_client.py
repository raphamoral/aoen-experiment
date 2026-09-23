from dataclasses import dataclass

from entities.client import Client
from use_cases.ports.repositories import ClientRepository


@dataclass
class CreateClientInput:
    name: str
    email: str
    company: str
    industry: str


class CreateClient:
    def __init__(self, repository: ClientRepository):
        self.repository = repository

    def execute(self, input: CreateClientInput) -> Client:
        if self.repository.find_by_email(input.email):
            raise ValueError(f"Email '{input.email}' is already registered")

        client = Client(
            name=input.name,
            email=input.email,
            company=input.company,
            industry=input.industry,
        )
        return self.repository.save(client)