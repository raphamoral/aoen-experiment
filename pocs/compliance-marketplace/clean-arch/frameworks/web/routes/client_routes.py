from fastapi import APIRouter, Depends, HTTPException

from adapters.presenters.schemas import ClientCreateRequest, ClientResponse
from adapters.controllers.client_controller import ClientController
from frameworks.web.dependencies import get_client_controller

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("/", response_model=ClientResponse, status_code=201)
def create_client(
    request: ClientCreateRequest,
    controller: ClientController = Depends(get_client_controller),
):
    try:
        return controller.create(request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))