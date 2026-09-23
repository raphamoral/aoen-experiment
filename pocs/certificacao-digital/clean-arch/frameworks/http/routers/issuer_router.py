from fastapi import APIRouter, Depends, HTTPException

from adapters.controllers.issuer_controller import IssuerController
from adapters.schemas.issuer_schema import IssuerResponse, RegisterIssuerRequest
from frameworks.http.dependencies import get_issuer_controller

router = APIRouter(prefix="/issuers", tags=["Issuers"])


@router.post("/", response_model=IssuerResponse, status_code=201)
def register_issuer(
    body: RegisterIssuerRequest,
    controller: IssuerController = Depends(get_issuer_controller),
) -> IssuerResponse:
    try:
        return controller.register(body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))