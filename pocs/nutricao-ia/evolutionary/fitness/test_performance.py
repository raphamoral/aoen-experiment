"""
Fitness Function: Desempenho.

Valida que endpoints críticos respondem dentro dos SLOs definidos em settings.
Threshold padrão: 500 ms (MAX_RESPONSE_TIME_MS).

Estes testes usam banco SQLite in-memory e MockAIProvider.
Se os tempos falharem mesmo em mock, investigue middlewares e queries N+1.
"""

import time

import pytest

from src.config import settings

USER_PAYLOAD = {
    "name": "Teste Performance",
    "email": "perf@nutriai.test",
    "birth_date": "1990-06-15",
    "sex": "masculino",
    "height_cm": 175.0,
    "weight_kg": 80.0,
    "activity_level": "moderado",
    "health_goals": "Perda de gordura e ganho de energia",
}


async def test_health_check_under_100ms(client):
    """Health check deve responder em menos de 100 ms — baseline de infraestrutura."""
    start = time.perf_counter()
    response = await client.get("/health")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert elapsed_ms < 100, (
        f"Health check levou {elapsed_ms:.1f} ms — esperado < 100 ms. "
        f"Verifique middleware de startup e inicialização do app."
    )


async def test_user_creation_within_slo(client):
    """Criação de usuário deve completar dentro do SLO (MAX_RESPONSE_TIME_MS)."""
    start = time.perf_counter()
    response = await client.post("/api/v1/users/", json=USER_PAYLOAD)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert response.status_code in (201, 409)
    assert elapsed_ms < settings.MAX_RESPONSE_TIME_MS, (
        f"Criação de usuário: {elapsed_ms:.1f} ms > {settings.MAX_RESPONSE_TIME_MS} ms (SLO). "
        f"Investigue queries na camada de repository."
    )


async def test_exam_list_within_slo(client):
    """Listagem de exames deve completar dentro do SLO."""
    start = time.perf_counter()
    response = await client.get("/api/v1/exams/?user_id=999")
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert elapsed_ms < settings.MAX_RESPONSE_TIME_MS, (
        f"Listagem de exames: {elapsed_ms:.1f} ms > {settings.MAX_RESPONSE_TIME_MS} ms (SLO)."
    )


async def test_response_time_header_present(client):
    """
    Middleware deve injetar X-Response-Time-Ms em todas as respostas.
    Header é consumido por ferramentas de observabilidade e pelo CI para alertas.
    """
    response = await client.get("/health")
    assert "x-response-time-ms" in response.headers, (
        "Header X-Response-Time-Ms ausente. "
        "Verifique se ResponseTimeMiddleware está registrado em main.py."
    )
    elapsed = float(response.headers["x-response-time-ms"])
    assert elapsed > 0, "X-Response-Time-Ms deve ser maior que zero."