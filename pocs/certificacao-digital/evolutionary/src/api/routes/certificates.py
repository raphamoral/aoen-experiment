import os

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.domain.schemas import CertificateCreate, CertificateResponse
from src.infrastructure.database import get_db
from src.services.certificate_service import get_certificate, issue_certificate, revoke_certificate

router = APIRouter()

# Decisão: API key simples (Last Responsible Moment).
# Evoluir para JWT/OAuth2 somente quando múltiplas organizações/papéis forem necessários.
_DEFAULT_API_KEY = "dev-api-key-change-in-production"


def _require_api_key(x_api_key: str = Header(...)):
    valid = os.getenv("API_KEY", _DEFAULT_API_KEY)
    if x_api_key != valid:
        raise HTTPException(status_code=401, detail="API key inválida")


@router.post(
    "/",
    response_model=CertificateResponse,
    status_code=201,
    dependencies=[Depends(_require_api_key)],
)
def issue(data: CertificateCreate, db: Session = Depends(get_db)):
    try:
        return issue_certificate(data, db)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get(
    "/{cert_id}",
    response_model=CertificateResponse,
    dependencies=[Depends(_require_api_key)],
)
def get_cert(cert_id: str, db: Session = Depends(get_db)):
    cert = get_certificate(cert_id, db)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    return cert


@router.delete(
    "/{cert_id}",
    response_model=CertificateResponse,
    dependencies=[Depends(_require_api_key)],
)
def revoke(cert_id: str, db: Session = Depends(get_db)):
    cert = revoke_certificate(cert_id, db)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    return cert