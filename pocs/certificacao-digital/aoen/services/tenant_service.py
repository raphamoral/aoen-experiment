"""
CONFIG-DRIVEN: gerenciamento de tenants e seus pares de chaves.

O fluxo de onboarding é fixo no código — apenas os parâmetros do tenant variam.
"""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from core.signing import generate_keypair
from models import Tenant
from services.certificate_service import PrivateKeyStore


class TenantService:
    def __init__(self, db: Session, key_store: PrivateKeyStore) -> None:
        self._db = db
        self._key_store = key_store

    def create(
        self,
        *,
        slug: str,
        name: str,
        config: dict | None = None,
    ) -> tuple[Tenant, str]:
        """
        Cria tenant, gera par de chaves Ed25519 e armazena:
        - chave pública no banco (visível para verificação)
        - chave privada no PrivateKeyStore (nunca exposta via API)

        Retorna (tenant, private_key_pem) — private_key_pem deve ser
        entregue ao tenant e descartado do servidor em produção.
        """
        if self._db.query(Tenant).filter(Tenant.slug == slug).first():
            raise ValueError(f"Slug '{slug}' já utilizado.")

        private_pem, public_pem = generate_keypair()

        tenant = Tenant(
            slug=slug,
            name=name,
            config_json=json.dumps(config) if config else None,
            public_key_pem=public_pem,
        )
        self._db.add(tenant)
        self._db.commit()
        self._db.refresh(tenant)

        self._key_store.set_private_key(tenant.id, private_pem)
        return tenant, private_pem

    def get_by_slug(self, slug: str) -> Tenant | None:
        return self._db.query(Tenant).filter(Tenant.slug == slug).first()

    def get_by_id(self, tenant_id: str) -> Tenant | None:
        return self._db.query(Tenant).filter(Tenant.id == tenant_id).first()

    def update_config(self, tenant_id: str, config_patch: dict) -> Tenant:
        tenant = self._db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} não encontrado.")
        existing = json.loads(tenant.config_json) if tenant.config_json else {}
        existing.update(config_patch)
        tenant.config_json = json.dumps(existing)
        self._db.commit()
        self._db.refresh(tenant)
        return tenant

    def list_all(self) -> list[Tenant]:
        return self._db.query(Tenant).all()