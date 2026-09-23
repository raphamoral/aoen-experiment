from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CertificateResponse, VerificationResponse
from app.services.certificate_service import get_by_hash

router = APIRouter(prefix="/verify", tags=["verification"])


@router.get(
    "/{verification_hash}",
    response_model=VerificationResponse,
    summary="Verificação pública de certificado",
)
def verify_certificate(verification_hash: str, db: Session = Depends(get_db)):
    cert = get_by_hash(db, verification_hash)

    if not cert:
        return VerificationResponse(valid=False, message="Certificado não encontrado.")

    if cert.expires_at and cert.expires_at < datetime.now(timezone.utc):
        return VerificationResponse(
            valid=False,
            certificate=CertificateResponse.model_validate(cert),
            message="Certificado expirado.",
        )

    return VerificationResponse(
        valid=True,
        certificate=CertificateResponse.model_validate(cert),
        message="Certificado válido e autêntico.",
    )