"""
Construção determinística do payload de certificado.

O hash é gerado a partir de campos canônicos em ordem fixa.
Isso garante que dois sistemas independentes — sem acesso ao banco —
possam recalcular e verificar o hash apenas com os dados públicos do certificado.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime


def build_certificate_payload(
    *,
    tenant_id: str,
    course_id: str,
    public_id: str,
    recipient_name: str,
    recipient_email: str,
    issued_at: datetime,
    workload_hours: int,
    issuer_name: str,
) -> bytes:
    """
    Serializa os campos canônicos em JSON ordenado e os converte para bytes.
    Esta função é o contrato público do formato de certificado.
    Nunca altere a ordem ou os nomes dos campos sem versionar o formato.
    """
    canonical = {
        "issuer_name": issuer_name,
        "tenant_id": tenant_id,
        "course_id": course_id,
        "public_id": public_id,
        "recipient_name": recipient_name,
        "recipient_email": recipient_email,
        "issued_at": issued_at.isoformat(),
        "workload_hours": workload_hours,
    }
    return json.dumps(canonical, sort_keys=True, ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()