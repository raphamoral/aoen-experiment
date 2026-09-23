from adapters.schemas.issuer_schema import IssuerResponse, RegisterIssuerRequest
from use_cases.register_issuer import RegisterIssuerInput, RegisterIssuerUseCase


class IssuerController:
    def __init__(self, register_uc: RegisterIssuerUseCase) -> None:
        self._register_uc = register_uc

    def register(self, request: RegisterIssuerRequest) -> IssuerResponse:
        output = self._register_uc.execute(
            RegisterIssuerInput(name=request.name, document=request.document)
        )
        issuer = output.issuer
        return IssuerResponse(id=issuer.id, name=issuer.name, document=issuer.document)