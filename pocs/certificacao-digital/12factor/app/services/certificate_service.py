import hashlib
import json
import secrets
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Certificate
from app.schemas import CertificateCreate

settings = get_settings()


def _generate_verification_hash(payload: dict) -> str:
    # Hash determinístico + salt para unicidade e resistência a enumeração
    salt = secrets.token_hex(16)
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(f"{salt}:{serialized}".encode()).hexdigest()


def create_certificate(db: Session, data: CertificateCreate) -> Certificate:
    now = datetime.now(timezone.utc)

    hash_input = {
        "recipient_email": data.recipient_email,
        "course_name": data.course_name,
        "issued_at": now.isoformat(),
        "nonce": secrets.token_hex(8),
    }

    cert = Certificate(
        verification_hash=_generate_verification_hash(hash_input),
        recipient_name=data.recipient_name,
        recipient_email=data.recipient_email,
        course_name=data.course_name,
        course_hours=data.course_hours,
        issuer=settings.certificate_issuer,
        issued_at=now,
        expires_at=data.expires_at,
    )

    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


def get_by_hash(db: Session, verification_hash: str) -> Optional[Certificate]:
    return (
        db.query(Certificate)
        .filter(Certificate.verification_hash == verification_hash)
        .first()
    )