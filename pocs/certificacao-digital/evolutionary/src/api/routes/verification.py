from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.domain.schemas import VerificationResult
from src.infrastructure.database import get_db
from src.services.verification_service import verify_by_hash

router = APIRouter()


@router.get("/{hash_value}", response_model=VerificationResult)
def verify(hash_value: str, db: Session = Depends(get_db)):
    """
    Endpoint público: autentica um certificado pelo seu hash HMAC-SHA256.
    Não requer autenticação. Nunca expõe dados pessoais (email).
    """
    return verify_by_hash(hash_value, db)