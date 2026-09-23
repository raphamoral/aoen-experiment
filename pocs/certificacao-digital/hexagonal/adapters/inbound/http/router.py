"""
HTTP adapter (driving side).

Translates HTTP verbs + JSON into port commands/queries and port results
back into HTTP responses.  The router has no business logic — it delegates
everything to the application service via inbound port interfaces.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from adapters.inbound.http.dependencies import get_certificate_service
from adapters.inbound.http.schemas import (
    CertificateSummaryResponse,
    IssueCertificateRequest,
    IssueCertificateResponse,
    ListCertificatesResponse,
    RevokeCertificateRequest,
    VerificationResponse,
)
from application.services.certificate_service import CertificateApplicationService
from domain.exceptions import (
    CertificateAlreadyRevokedError,
    CertificateNotFoundError,
    DuplicateCertificateError,
)
from ports.inbound.issue_certificate_port import IssueCertificateCommand
from ports.inbound.revoke_certificate_port import RevokeCertificateCommand

router = APIRouter()


@router.post(
    "/certificates",
    response_model=IssueCertificateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Issue a digital certificate",
    tags=["Certificates"],
)
def issue_certificate(
    request: IssueCertificateRequest,
    service: CertificateApplicationService = Depends(get_certificate_service),
) -> IssueCertificateResponse:
    try:
        result = service.issue_certificate(
            IssueCertificateCommand(
                student_id=request.student_id,
                student_name=request.student_name,
                student_email=request.student_email,
                course_id=request.course_id,
                course_name=request.course_name,
                issuer_name=request.issuer_name,
                duration_hours=request.duration_hours,
            )
        )
    except DuplicateCertificateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return IssueCertificateResponse(
        certificate_id=result.certificate_id,
        certificate_hash=result.certificate_hash,
        issued_at=result.issued_at,
        verification_url=result.verification_url,
    )


@router.get(
    "/verify/{certificate_hash}",
    response_model=VerificationResponse,
    summary="Public certificate verification by hash",
    tags=["Public Verification"],
)
def verify_by_hash(
    certificate_hash: str,
    service: CertificateApplicationService = Depends(get_certificate_service),
) -> VerificationResponse:
    result = service.verify_by_hash(certificate_hash)
    return VerificationResponse(
        is_valid=result.is_valid,
        certificate_id=result.certificate_id,
        student_name=result.student_name,
        course_name=result.course_name,
        issuer_name=result.issuer_name,
        duration_hours=result.duration_hours,
        issued_at=result.issued_at,
        revocation_reason=result.revocation_reason,
    )


@router.get(
    "/certificates/{certificate_id}",
    response_model=VerificationResponse,
    summary="Get certificate details by ID",
    tags=["Certificates"],
)
def get_certificate(
    certificate_id: str,
    service: CertificateApplicationService = Depends(get_certificate_service),
) -> VerificationResponse:
    result = service.verify_by_id(certificate_id)
    if not result.certificate_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate not found: {certificate_id}",
        )
    return VerificationResponse(
        is_valid=result.is_valid,
        certificate_id=result.certificate_id,
        student_name=result.student_name,
        course_name=result.course_name,
        issuer_name=result.issuer_name,
        duration_hours=result.duration_hours,
        issued_at=result.issued_at,
        revocation_reason=result.revocation_reason,
    )


@router.delete(
    "/certificates/{certificate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a certificate",
    tags=["Certificates"],
)
def revoke_certificate(
    certificate_id: str,
    request: RevokeCertificateRequest,
    service: CertificateApplicationService = Depends(get_certificate_service),
) -> None:
    try:
        service.revoke_certificate(
            RevokeCertificateCommand(
                certificate_id=certificate_id,
                reason=request.reason,
            )
        )
    except CertificateNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except CertificateAlreadyRevokedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/students/{student_id}/certificates",
    response_model=ListCertificatesResponse,
    summary="List all certificates for a student",
    tags=["Certificates"],
)
def list_student_certificates(
    student_id: str,
    service: CertificateApplicationService = Depends(get_certificate_service),
) -> ListCertificatesResponse:
    result = service.list_by_student(student_id)
    return ListCertificatesResponse(
        certificates=[
            CertificateSummaryResponse(
                id=cert.id,
                course_name=cert.course_name,
                issuer_name=cert.issuer_name,
                duration_hours=cert.duration_hours,
                issued_at=cert.issued_at,
                is_valid=cert.is_valid,
                certificate_hash=cert.certificate_hash,
            )
            for cert in result.certificates
        ],
        total=result.total,
    )