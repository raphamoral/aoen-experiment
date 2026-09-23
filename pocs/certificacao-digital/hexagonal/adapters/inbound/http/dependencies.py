"""
Composition root for the HTTP adapter.

This module is the only place that knows about concrete adapter implementations.
It wires outbound adapters to the application service and exposes a FastAPI
dependency so every request gets a properly scoped service instance.
"""

import os

from fastapi import Depends
from sqlalchemy.orm import Session

from adapters.outbound.hashing.sha256_hashing_service import SHA256HashingService
from adapters.outbound.notification.smtp_notification_service import (
    SmtpConfig,
    SmtpNotificationService,
)
from adapters.outbound.persistence.database import get_db
from adapters.outbound.persistence.sqlalchemy_certificate_repository import (
    SQLAlchemyCertificateRepository,
)
from adapters.outbound.storage.local_certificate_storage import LocalCertificateStorage
from application.services.certificate_service import CertificateApplicationService

# ---------------------------------------------------------------------------
# Stateless, singleton adapters — instantiated once at module load
# ---------------------------------------------------------------------------

_hashing_service = SHA256HashingService()

_smtp_config = SmtpConfig(
    host=os.getenv("SMTP_HOST", "localhost"),
    port=int(os.getenv("SMTP_PORT", "587")),
    username=os.getenv("SMTP_USER", ""),
    password=os.getenv("SMTP_PASSWORD", ""),
    sender_email=os.getenv("SMTP_SENDER", "noreply@certification.local"),
    use_tls=os.getenv("SMTP_TLS", "true").lower() == "true",
)
_notification_service = SmtpNotificationService(config=_smtp_config)

_storage = LocalCertificateStorage(
    storage_dir=os.getenv("STORAGE_DIR", "./certificates_storage")
)

_base_url = os.getenv("BASE_URL", "http://localhost:8000")


# ---------------------------------------------------------------------------
# Per-request dependency — repository gets a fresh, scoped DB session
# ---------------------------------------------------------------------------


def get_certificate_service(
    db: Session = Depends(get_db),
) -> CertificateApplicationService:
    repository = SQLAlchemyCertificateRepository(session=db)
    return CertificateApplicationService(
        repository=repository,
        hashing_service=_hashing_service,
        notification_service=_notification_service,
        storage=_storage,
        base_url=_base_url,
    )