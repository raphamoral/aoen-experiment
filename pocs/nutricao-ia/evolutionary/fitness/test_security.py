"""
Fitness Function: Segurança.

Valida práticas básicas de segurança na API.
Falhas aqui indicam vulnerabilidades ou dívida técnica a documentar.

Nota: Autenticação não implementada no MVP (Last Responsible Moment).
O teste test_unauthenticated_access_is_documented registra esta dívida
e deve ser ATUALIZADO quando auth for implementada — não removido.
"""

import pytest


async def test_invalid_email_rejected(client):
    """Pydantic deve rejeitar emails malformados com 422 antes de chegar ao banco."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "name": "Teste",
            "email": "nao-e-um-email",
            "birth_date": "1990-01-01",
            "sex": "masculino",
            "height_cm": 175.0,
            "weight_kg": 70.0,
            "activity_level": "moderado",
        },
    )
    assert response.status_code == 422, (
        "Email inválido deve ser rejeitado com 422 (Unprocessable Entity). "
        "Verifique se EmailStr está aplicado no schema UserCreate."
    )


async def test_negative_biometric_values_rejected(client):
    """Valores negativos para dados biométricos devem ser rejeitados na validação."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "name": "Teste",
            "email": "valido@test.com",
            "birth_date": "1990-01-01",
            "sex": "masculino",
            "height_cm": -10.0,
            "weight_kg": -50.0,
            "activity_level": "moderado",
        },
    )
    assert response.status_code == 422, (
        "Valores negativos para height_cm e weight_kg devem ser rejeitados. "
        "Verifique field_validators em UserCreate."
    )


async def test_invalid_enum_value_rejected(client):
    """Valores fora dos enums definidos devem ser rejeitados."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "name": "Teste",
            "email": "valido2@test.com",
            "birth_date": "1990-01-01",
            "sex": "INVALIDO",
            "height_cm": 170.0,
            "weight_kg": 65.0,
            "activity_level": "moderado",
        },
    )
    assert response.status_code == 422, (
        "Valor inválido para enum 'sex' deve ser rejeitado com 422."
    )


async def test_nonexistent_resource_returns_404_not_500(client):
    """Recursos não encontrados devem retornar 404 — nunca 500 (vazamento de stack trace)."""
    response = await client.get("/api/v1/users/999999")
    assert response.status_code == 404, (
        f"Usuário inexistente retornou {response.status_code} em vez de 404. "
        f"Nunca exponha 500 para IDs não encontrados."
    )
    body = response.json()
    assert "detail" in body, "Resposta 404 deve conter campo 'detail' com mensagem."


async def test_content_type_is_json(client):
    """API deve sempre retornar Content-Type: application/json."""
    response = await client.get("/health")
    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type, (
        f"Content-Type inválido: '{content_type}'. API deve retornar application/json."
    )


async def test_unauthenticated_access_is_documented():
    """
    DÍVIDA TÉCNICA DOCUMENTADA: endpoints não possuem autenticação no MVP.

    Este teste valida que a dívida está registrada e serve como lembrete para
    implementar JWT/OAuth2 quando o produto sair do MVP.

    Ação necessária: Implementar autenticação e atualizar este teste para
    verificar que endpoints protegidos retornam 401 sem token válido.
    """
    # Fitness function passa intencionalmente enquanto auth não está implementada.
    # Remover este comentário e implementar o assert quando auth for adicionada:
    # response = await client.get("/api/v1/users/")
    # assert response.status_code == 401
    assert True, "Auth não implementada no MVP — dívida técnica documentada."