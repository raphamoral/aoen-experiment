"""
MULTI-INTERFACE: endpoint público de verificação — sem autenticação.

Este router é montado fora do prefixo /api/v1 para ter URLs limpas
compartilháveis (ex: https://cert.example.com/verify/abc-123).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.verification_service import VerificationResult, VerificationService

router = APIRouter(tags=["verification"])


class VerificationResponse(BaseModel):
    status: str
    message: str
    public_id: str | None
    recipient_name: str | None
    course_title: str | None
    issued_at: str | None
    expires_at: str | None
    issuer: str | None
    signature_valid: bool
    verification_url: str
    qr_code_base64: str | None


@router.get("/verify/{public_id}", response_model=VerificationResponse)
def verify_certificate(public_id: str, request: Request, db: Session = Depends(get_db)):
    from config import TenantConfig

    svc = VerificationService(db)
    requester_ip = request.client.host if request.client else None
    result = svc.verify(public_id, requester_ip=requester_ip)

    cert = result.certificate
    if cert is None:
        return VerificationResponse(
            status=result.status,
            message=result.message,
            public_id=None,
            recipient_name=None,
            course_title=None,
            issued_at=None,
            expires_at=None,
            issuer=None,
            signature_valid=False,
            verification_url=result.verification_url,
            qr_code_base64=None,
        )

    cfg = TenantConfig.from_json(cert.tenant.config_json if cert.tenant else None)

    return VerificationResponse(
        status=result.status,
        message=result.message,
        public_id=cert.public_id,
        recipient_name=cert.recipient_name,
        course_title=cert.course.title if cert.course else None,
        issued_at=cert.issued_at.isoformat(),
        expires_at=cert.expires_at.isoformat() if cert.expires_at else None,
        issuer=cfg.get("issuer_name"),
        signature_valid=result.signature_valid,
        verification_url=result.verification_url,
        qr_code_base64=result.qr_code_base64,
    )