from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CertificateCreate, CertificateResponse
from app.services.certificate_service import create_certificate

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.post(
    "/",
    response_model=CertificateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Emitir certificado digital",
)
def issue_certificate(payload: CertificateCreate, db: Session = Depends(get_db)):
    return create_certificate(db, payload)