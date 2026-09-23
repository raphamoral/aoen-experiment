from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from adapters.controllers.client_controller import ClientController, RegisterClientRequest
from frameworks.http.dependencies import get_client_controller

router = APIRouter(prefix="/clients", tags=["Clients"])

ClientDep = Annotated[ClientController, Depends(get_client_controller)]


class RegisterClientBody(BaseModel):
    company_name: str
    email: str
    cnpj: str
    industry: str
    contact_name: str


@router.post("/", status_code=status.HTTP_201_CREATED)
def register_client(body: RegisterClientBody, controller: ClientDep) -> dict:
    try:
        return controller.register(
            RegisterClientRequest(
                company_name=body.company_name,
                email=body.email,
                cnpj=body.cnpj,
                industry=body.industry,
                contact_name=body.contact_name,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))