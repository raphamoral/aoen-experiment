from sqlalchemy.orm import Session

from src.domain.models import Certificate
from src.domain.schemas import VerificationResult


def verify_by_hash(hash_value: str, db: Session) -> VerificationResult:
    cert = (
        db.query(Certificate)
        .filter(Certificate.verification_hash == hash_value)
        .first()
    )

    if not cert:
        return VerificationResult(
            valid=False,
            verification_hash=hash_value,
            message="Certificado não encontrado",
        )

    if cert.revoked:
        return VerificationResult(
            valid=False,
            verification_hash=hash_value,
            revoked=True,
            message="Certificado foi revogado",
        )

    return VerificationResult(
        valid=True,
        course_name=cert.course.name,
        recipient_name=cert.recipient_name,
        issued_at=cert.issued_at,
        verification_hash=hash_value,
        message="Certificado válido",
    )