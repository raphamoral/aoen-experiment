from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from src.domain.models import Certificate, Course
from src.domain.schemas import CertificateCreate
from src.infrastructure.hash_service import generate_certificate_hash


def issue_certificate(data: CertificateCreate, db: Session) -> Certificate:
    course = db.query(Course).filter(Course.id == data.course_id, Course.active.is_(True)).first()
    if not course:
        raise ValueError(f"Curso '{data.course_id}' não encontrado ou inativo")

    issued_at = datetime.utcnow()
    verification_hash = generate_certificate_hash(
        course_id=data.course_id,
        recipient_email=data.recipient_email,
        issued_at=issued_at.isoformat(),
    )

    cert = Certificate(
        course_id=data.course_id,
        recipient_name=data.recipient_name,
        recipient_email=data.recipient_email,
        issued_at=issued_at,
        verification_hash=verification_hash,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


def revoke_certificate(cert_id: str, db: Session) -> Optional[Certificate]:
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        return None
    cert.revoked = True
    cert.revoked_at = datetime.utcnow()
    db.commit()
    db.refresh(cert)
    return cert


def get_certificate(cert_id: str, db: Session) -> Optional[Certificate]:
    return db.query(Certificate).filter(Certificate.id == cert_id).first()