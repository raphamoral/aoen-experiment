from entities.client import Client
from use_cases.client.create_client import CreateClient, CreateClientInput
from adapters.presenters.schemas import ClientCreateRequest, ClientResponse


class ClientController:
    def __init__(self, create_uc: CreateClient):
        self.create_uc = create_uc

    def create(self, request: ClientCreateRequest) -> ClientResponse:
        client = self.create_uc.execute(
            CreateClientInput(
                name=request.name,
                email=request.email,
                company=request.company,
                industry=request.industry,
            )
        )
        return self._to_response(client)

    def _to_response(self, c: Client) -> ClientResponse:
        return ClientResponse(
            id=c.id,
            name=c.name,
            email=c.email,
            company=c.company,
            industry=c.industry,
            is_active=c.is_active,
        )