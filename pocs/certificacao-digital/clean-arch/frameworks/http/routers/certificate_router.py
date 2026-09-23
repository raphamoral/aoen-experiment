from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from adapters.controllers.certificate_controller import CertificateController
from adapters.schemas.certificate_schema import (
    CertificateResponse,
    IssueCertificateRequest,
    RevokeCertificateRequest,
    VerificationResponse,
)
from frameworks.http.dependencies import get_certificate_controller

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.post("/", response_model=CertificateResponse, status_code=201)
def issue_certificate(
    body: IssueCertificateRequest,
    controller: CertificateController = Depends(get_certificate_controller),
) -> CertificateResponse:
    try:
        return controller.issue(body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/verify/{verification_hash}", response_model=VerificationResponse, tags=["Public"])
def verify_certificate(
    verification_hash: str,
    controller: CertificateController = Depends(get_certificate_controller),
) -> VerificationResponse:
    return controller.verify(verification_hash)


@router.patch("/{certificate_id}/revoke", response_model=CertificateResponse)
def revoke_certificate(
    certificate_id: UUID,
    body: RevokeCertificateRequest,
    controller: CertificateController = Depends(get_certificate_controller),
) -> CertificateResponse:
    try:
        return controller.revoke(certificate_id, body)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/student/{student_id}", response_model=list[CertificateResponse])
def list_student_certificates(
    student_id: UUID,
    controller: CertificateController = Depends(get_certificate_controller),
) -> list[CertificateResponse]:
    try:
        return controller.list_by_student(student_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))