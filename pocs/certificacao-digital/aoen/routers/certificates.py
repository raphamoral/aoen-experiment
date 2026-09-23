from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.certificate_service import CertificateService, CertificateServiceError, get_key_store

router = APIRouter(prefix="/certificates", tags=["certificates"])


class CertificateIssueRequest(BaseModel):
    tenant_id: str
    course_id: str
    recipient_name: str
    recipient_email: str
    recipient_document: str | None = None
    extra_metadata: dict | None = None


class CertificateRevokeRequest(BaseModel):
    reason: str


class CertificateResponse(BaseModel):
    id: str
    public_id: str
    tenant_id: str
    course_id: str
    recipient_name: str
    recipient_email: str
    recipient_document: str | None
    payload_hash: str
    issued_at: str
    expires_at: str | None
    is_revoked: bool
    revocation_reason: str | None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_dates(cls, cert) -> "CertificateResponse":
        return cls(
            id=cert.id,
            public_id=cert.public_id,
            tenant_id=cert.tenant_id,
            course_id=cert.course_id,
            recipient_name=cert.recipient_name,
            recipient_email=cert.recipient_email,
            recipient_document=cert.recipient_document,
            payload_hash=cert.payload_hash,
            issued_at=cert.issued_at.isoformat(),
            expires_at=cert.expires_at.isoformat() if cert.expires_at else None,
            is_revoked=cert.is_revoked,
            revocation_reason=cert.revocation_reason,
        )


@router.post("/", response_model=CertificateResponse, status_code=status.HTTP_201_CREATED)
def issue_certificate(body: CertificateIssueRequest, db: Session = Depends(get_db)):
    svc = CertificateService(db, get_key_store())
    try:
        cert = svc.issue(
            tenant_id=body.tenant_id,
            course_id=body.course_id,
            recipient_name=body.recipient_name,
            recipient_email=body.recipient_email,
            recipient_document=body.recipient_document,
            extra_metadata=body.extra_metadata,
        )
    except CertificateServiceError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return CertificateResponse.from_orm_with_dates(cert)


@router.get("/", response_model=list[CertificateResponse])
def list_certificates(tenant_id: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    svc = CertificateService(db, get_key_store())
    certs = svc.list_by_tenant(tenant_id, skip=skip, limit=limit)
    return [CertificateResponse.from_orm_with_dates(c) for c in certs]


@router.get("/{public_id}", response_model=CertificateResponse)
def get_certificate(public_id: str, db: Session = Depends(get_db)):
    svc = CertificateService(db, get_key_store())
    cert = svc.get_by_public_id(public_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificado não encontrado.")
    return CertificateResponse.from_orm_with_dates(cert)


@router.post("/{public_id}/revoke", response_model=CertificateResponse)
def revoke_certificate(
    public_id: str,
    body: CertificateRevokeRequest,
    tenant_id: str,
    db: Session = Depends(get_db),
):
    svc = CertificateService(db, get_key_store())
    try:
        cert = svc.revoke(public_id=public_id, tenant_id=tenant_id, reason=body.reason)
    except CertificateServiceError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return CertificateResponse.from_orm_with_dates(cert)