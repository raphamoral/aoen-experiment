"""
Fitness Function: Security Characteristics
───────────────────────────────────────────
Protege três propriedades de segurança invariantes:

  1. PII (email) nunca aparece no endpoint público /verify/
  2. Operações de escrita exigem autenticação válida
  3. Um hash adulterado NUNCA valida como verdadeiro

Estas funções devem rodar em todo PR — são a última linha de defesa
antes que uma regressão de segurança chegue à produção.
"""

import pytest


def test_public_verify_does_not_expose_email(client, sample_certificate):
    """PII: endpoint público não deve vazar o email do destinatário."""
    h = sample_certificate["verification_hash"]
    body = client.get(f"/verify/{h}").json()

    assert "email" not in body, f"Campo 'email' exposto: {body}"
    assert "recipient_email" not in body, f"Campo 'recipient_email' exposto: {body}"

    # Verificação defensiva: nenhum valor contém '@'
    for key, value in body.items():
        if isinstance(value, str) and "@" in value:
            pytest.fail(f"Possível email exposto em campo '{key}': {value!r}")


def test_issue_without_api_key_is_rejected(client, sample_course):
    """Auth: criar certificado sem header x-api-key deve retornar 4xx."""
    resp = client.post(
        "/certificates/",
        json={
            "course_id": sample_course["id"],
            "recipient_name": "Sem Auth",
            "recipient_email": "noauth@example.com",
        },
        # header ausente intencionalmente
    )
    assert resp.status_code in (401, 422), (
        f"Esperado 401 ou 422 sem autenticação, recebido {resp.status_code}"
    )


def test_issue_with_wrong_api_key_is_rejected(client, sample_course):
    """Auth: API key incorreta deve retornar 401 (não 200, não 403)."""
    resp = client.post(
        "/certificates/",
        json={
            "course_id": sample_course["id"],
            "recipient_name": "Intruso",
            "recipient_email": "intruso@evil.com",
        },
        headers={"x-api-key": "totally-wrong-key-000"},
    )
    assert resp.status_code == 401, (
        f"API key incorreta deveria retornar 401, recebido {resp.status_code}"
    )


def test_tampered_hash_is_invalid(client, sample_certificate):
    """Integridade: modificar qualquer byte do hash deve invalidar o certificado."""
    original = sample_certificate["verification_hash"]
    # Adultera os últimos 4 caracteres — qualquer diferença deve falhar
    tampered = original[:-4] + ("0000" if original[-4:] != "0000" else "ffff")

    body = client.get(f"/verify/{tampered}").json()
    assert body["valid"] is False, (
        "Hash adulterado retornou válido — falha crítica de integridade!"
    )


def test_revoked_certificate_is_invalid(client, api_headers, sample_certificate):
    """Revogação: certificado revogado deve retornar valid=False na verificação pública."""
    cert_id = sample_certificate["id"]
    h = sample_certificate["verification_hash"]

    revoke_resp = client.delete(f"/certificates/{cert_id}", headers=api_headers)
    assert revoke_resp.status_code == 200

    verify_resp = client.get(f"/verify/{h}").json()
    assert verify_resp["valid"] is False
    assert verify_resp["revoked"] is True


def test_delete_without_api_key_is_rejected(client, sample_certificate):
    """Auth: revogar certificado sem autenticação deve falhar."""
    cert_id = sample_certificate["id"]
    resp = client.delete(f"/certificates/{cert_id}")
    assert resp.status_code in (401, 422)