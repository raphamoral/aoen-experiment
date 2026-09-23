"""
NÚCLEO (VALOR) — orquestração da emissão de certificados.

Service Layer desacoplada: não conhece FastAPI, não conhece HTTP.
Pode ser chamada por CLI, worker assíncrono, ou outro microsserviço.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from config import TenantConfig
from core.hash_chain import build_certificate_payload, sha256_hex
from core.signing import sign, verify
from models import Certificate, Course, Tenant


class CertificateServiceError(Exception):
    pass


class CertificateService:
    def __init__(self, db: Session, private_key_store: "PrivateKeyStore") -> None:
        self._db = db
        self._key_store = private_key_store

    # ── Emissão ──────────────────────────────────────────────────────────────

    def issue(
        self,
        *,
        tenant_id: str,
        course_id: str,
        recipient_name: str,
        recipient_email: str,
        recipient_document: str | None = None,
        extra_metadata: dict | None = None,
    ) -> Certificate:
        tenant = self._get_tenant(tenant_id)
        course = self._get_course(course_id, tenant_id)
        cfg = TenantConfig.from_json(tenant.config_json)

        self._check_monthly_limit(tenant_id, cfg)

        private_key_pem = self._key_store.get_private_key(tenant_id)
        if not private_key_pem:
            raise CertificateServiceError(
                f"Tenant {tenant_id} não possui chave privada configurada."
            )

        issued_at = datetime.now(timezone.utc)
        validity_years: int = cfg.get("validity_years")
        expires_at = issued_at + timedelta(days=365 * validity_years)
        issuer_name: str = cfg.get("issuer_name")

        # Gera public_id antes para incluir no payload
        import uuid
        public_id = str(uuid.uuid4())

        payload_bytes = build_certificate_payload(
            tenant_id=tenant_id,
            course_id=course_id,
            public_id=public_id,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            issued_at=issued_at,
            workload_hours=course.workload_hours,
            issuer_name=issuer_name,
        )

        payload_hash = sha256_hex(payload_bytes)
        signature = sign(payload_bytes, private_key_pem)

        cert = Certificate(
            tenant_id=tenant_id,
            course_id=course_id,
            public_id=public_id,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            recipient_document=recipient_document,
            payload_hash=payload_hash,
            signature=signature,
            issued_at=issued_at,
            expires_at=expires_at,
            metadata_json=json.dumps(extra_metadata) if extra_metadata else None,
        )
        self._db.add(cert)
        self._db.commit()
        self._db.refresh(cert)
        return cert

    # ── Revogação ────────────────────────────────────────────────────────────

    def revoke(
        self, *, public_id: str, tenant_id: str, reason: str
    ) -> Certificate:
        cert = self._get_certificate_by_public_id(public_id, tenant_id)
        if cert.is_revoked:
            raise CertificateServiceError("Certificado já revogado.")
        cert.is_revoked = True
        cert.revocation_reason = reason
        cert.revoked_at = datetime.now(timezone.utc)
        self._db.commit()
        self._db.refresh(cert)
        return cert

    # ── Consulta ─────────────────────────────────────────────────────────────

    def get_by_public_id(self, public_id: str) -> Certificate | None:
        return (
            self._db.query(Certificate)
            .filter(Certificate.public_id == public_id)
            .first()
        )

    def list_by_tenant(self, tenant_id: str, skip: int = 0, limit: int = 50) -> list[Certificate]:
        return (
            self._db.query(Certificate)
            .filter(Certificate.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ── Helpers privados ─────────────────────────────────────────────────────

    def _get_tenant(self, tenant_id: str) -> Tenant:
        tenant = self._db.query(Tenant).filter(Tenant.id == tenant_id, Tenant.is_active == True).first()
        if not tenant:
            raise CertificateServiceError(f"Tenant {tenant_id} não encontrado ou inativo.")
        return tenant

    def _get_course(self, course_id: str, tenant_id: str) -> Course:
        course = (
            self._db.query(Course)
            .filter(Course.id == course_id, Course.tenant_id == tenant_id, Course.is_active == True)
            .first()
        )
        if not course:
            raise CertificateServiceError(f"Curso {course_id} não encontrado.")
        return course

    def _get_certificate_by_public_id(self, public_id: str, tenant_id: str) -> Certificate:
        cert = (
            self._db.query(Certificate)
            .filter(Certificate.public_id == public_id, Certificate.tenant_id == tenant_id)
            .first()
        )
        if not cert:
            raise CertificateServiceError(f"Certificado {public_id} não encontrado.")
        return cert

    def _check_monthly_limit(self, tenant_id: str, cfg: TenantConfig) -> None:
        from datetime import date
        start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        count = (
            self._db.query(Certificate)
            .filter(
                Certificate.tenant_id == tenant_id,
                Certificate.issued_at >= start_of_month,
            )
            .count()
        )
        limit: int = cfg.get("max_certificates_per_month")
        if count >= limit:
            raise CertificateServiceError(
                f"Limite mensal de {limit} certificados atingido para este tenant."
            )


# ── Abstração do armazenamento de chaves privadas ────────────────────────────
# ISOLAMENTO: chaves privadas nunca ficam no banco junto com dados públicos.
# Em produção, substitua por HashiCorp Vault, AWS KMS, ou similar.

class PrivateKeyStore:
    """
    Interface simples substituível. Em desenvolvimento usa variável de ambiente;
    em produção injete uma implementação que fala com um KMS.
    """

    def __init__(self) -> None:
        self._keys: dict[str, str] = {}

    def set_private_key(self, tenant_id: str, private_key_pem: str) -> None:
        self._keys[tenant_id] = private_key_pem

    def get_private_key(self, tenant_id: str) -> str | None:
        return self._keys.get(tenant_id)


# Singleton de desenvolvimento — em produção, use injeção de dependência real
_dev_key_store = PrivateKeyStore()


def get_key_store() -> PrivateKeyStore:
    return _dev_key_store