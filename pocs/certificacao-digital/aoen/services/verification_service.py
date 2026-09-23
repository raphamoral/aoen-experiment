"""
MULTI-INTERFACE: verificação pública — sem autenticação, sem tenant context.

Qualquer pessoa com o public_id (ou QR code) pode verificar um certificado.
Este serviço é a interface pública do produto; é o que justifica a confiança.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from config import TenantConfig, get_settings
from core.hash_chain import build_certificate_payload, sha256_hex
from core.qr_generator import build_verification_url, generate_qr_base64
from core.signing import verify as verify_signature
from models import Certificate, Tenant, VerificationLog


class VerificationResult:
    def __init__(
        self,
        *,
        status: str,
        certificate: Certificate | None,
        signature_valid: bool,
        qr_code_base64: str | None,
        verification_url: str,
        message: str,
    ) -> None:
        self.status = status
        self.certificate = certificate
        self.signature_valid = signature_valid
        self.qr_code_base64 = qr_code_base64
        self.verification_url = verification_url
        self.message = message


class VerificationService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._settings = get_settings()

    def verify(self, public_id: str, requester_ip: str | None = None) -> VerificationResult:
        cert = (
            self._db.query(Certificate)
            .filter(Certificate.public_id == public_id)
            .first()
        )
        verification_url = build_verification_url(self._settings.base_url, public_id)

        if not cert:
            return VerificationResult(
                status="not_found",
                certificate=None,
                signature_valid=False,
                qr_code_base64=None,
                verification_url=verification_url,
                message="Certificado não encontrado.",
            )

        tenant = self._db.query(Tenant).filter(Tenant.id == cert.tenant_id).first()
        cfg = TenantConfig.from_json(tenant.config_json if tenant else None)
        issuer_name: str = cfg.get("issuer_name")

        # Recalcula payload a partir dos dados do banco e verifica assinatura
        payload_bytes = build_certificate_payload(
            tenant_id=cert.tenant_id,
            course_id=cert.course_id,
            public_id=cert.public_id,
            recipient_name=cert.recipient_name,
            recipient_email=cert.recipient_email,
            issued_at=cert.issued_at,
            workload_hours=cert.course.workload_hours,
            issuer_name=issuer_name,
        )
        recalculated_hash = sha256_hex(payload_bytes)
        hash_intact = recalculated_hash == cert.payload_hash

        public_key_pem = tenant.public_key_pem if tenant else None
        signature_valid = (
            verify_signature(payload_bytes, cert.signature, public_key_pem)
            if public_key_pem
            else False
        )

        # Status lógico
        now = datetime.now(timezone.utc)
        if cert.is_revoked:
            status = "revoked"
            message = f"Certificado revogado em {cert.revoked_at}. Motivo: {cert.revocation_reason}"
        elif cert.expires_at and cert.expires_at < now:
            status = "expired"
            message = "Certificado expirado."
        elif not signature_valid or not hash_intact:
            status = "tampered"
            message = "Assinatura ou hash inválidos — certificado pode ter sido adulterado."
        else:
            status = "valid"
            message = "Certificado válido e autêntico."

        qr = generate_qr_base64(verification_url)

        # ISOLAMENTO: log para billing/analytics por tenant
        self._db.add(
            VerificationLog(
                certificate_id=cert.id,
                requester_ip=requester_ip,
                result=status,
            )
        )
        self._db.commit()

        return VerificationResult(
            status=status,
            certificate=cert,
            signature_valid=signature_valid,
            qr_code_base64=qr,
            verification_url=verification_url,
            message=message,
        )