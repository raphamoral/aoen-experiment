from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


# ─── MULTI-TENANT ────────────────────────────────────────────────────────────

class Tenant(Base):
    """
    MULTI-INTERFACE: cada tenant é um mercado independente.
    A mesma lógica de certificação serve escolas, empresas, eventos.
    """
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # CONFIG-DRIVEN: JSON plano de configurações por tenant
    config_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    # ISOLAMENTO: chave pública do par Ed25519 gerado no core/
    public_key_pem: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    courses: Mapped[list["Course"]] = relationship(back_populates="tenant")
    certificates: Mapped[list["Certificate"]] = relationship(back_populates="tenant")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    workload_hours: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    tenant: Mapped["Tenant"] = relationship(back_populates="courses")
    certificates: Mapped[list["Certificate"]] = relationship(back_populates="course")


class Certificate(Base):
    """
    NÚCLEO (VALOR): a entidade central. Contém a assinatura criptográfica
    que garante autenticidade e permite verificação pública sem depender
    de nenhum servidor de terceiros.
    """
    __tablename__ = "certificates"
    __table_args__ = (
        UniqueConstraint("public_id", name="uq_certificate_public_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"), nullable=False)

    # Dados do recipiente — sem tabela separada de Student para manter o
    # isolamento: o core não precisa saber nada sobre gestão de usuários.
    recipient_name: Mapped[str] = mapped_column(String(512), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(512), nullable=False)
    recipient_document: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # NÚCLEO: identidade e prova criptográfica
    public_id: Mapped[str] = mapped_column(String(36), default=_new_uuid, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    signature: Mapped[str] = mapped_column(Text, nullable=False)

    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    revocation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Metadados extras livres por tenant (JSON)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="certificates")
    course: Mapped["Course"] = relationship(back_populates="certificates")
    verification_logs: Mapped[list["VerificationLog"]] = relationship(
        back_populates="certificate"
    )


class VerificationLog(Base):
    """
    ISOLAMENTO: log de verificações permite medir custo de infraestrutura
    por tenant e cobrar pelo uso real.
    """
    __tablename__ = "verification_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    certificate_id: Mapped[str] = mapped_column(
        ForeignKey("certificates.id"), nullable=False
    )
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    requester_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    result: Mapped[str] = mapped_column(String(32), nullable=False)  # valid|revoked|expired

    certificate: Mapped["Certificate"] = relationship(back_populates="verification_logs")