"""
Fitness Function: Response Time SLA
─────────────────────────────────────
Protege: endpoints críticos devem responder abaixo dos limiares definidos.

Os thresholds são contratos arquiteturais explícitos.
Aumentar um threshold requer decisão consciente — não é um fix trivial.
Ao falhar, investigue: N+1 queries, falta de índice, lógica pesada no handler.
"""

import time

import pytest

# ms — contratos explícitos por endpoint
SLA: dict[str, int] = {
    "health": 50,
    "list_courses": 200,
    "verify_miss": 200,
    "verify_hit": 200,
}


def _elapsed_ms(start: float) -> float:
    return (time.perf_counter() - start) * 1_000


def test_health_sla(client):
    t = time.perf_counter()
    resp = client.get("/health")
    ms = _elapsed_ms(t)

    assert resp.status_code == 200
    assert ms < SLA["health"], f"/health: {ms:.1f}ms > SLA {SLA['health']}ms"


def test_list_courses_sla(client):
    t = time.perf_counter()
    resp = client.get("/courses/")
    ms = _elapsed_ms(t)

    assert resp.status_code == 200
    assert ms < SLA["list_courses"], f"GET /courses/: {ms:.1f}ms > SLA {SLA['list_courses']}ms"


def test_verify_miss_sla(client):
    """Hash inexistente: verifica que a busca indexada não degrada."""
    fake_hash = "a" * 64
    t = time.perf_counter()
    resp = client.get(f"/verify/{fake_hash}")
    ms = _elapsed_ms(t)

    assert resp.status_code == 200
    assert resp.json()["valid"] is False
    assert ms < SLA["verify_miss"], f"GET /verify/miss: {ms:.1f}ms > SLA {SLA['verify_miss']}ms"


def test_verify_hit_sla(client, sample_certificate):
    """Hash válido: caminho feliz deve ser o mais rápido."""
    h = sample_certificate["verification_hash"]
    t = time.perf_counter()
    resp = client.get(f"/verify/{h}")
    ms = _elapsed_ms(t)

    assert resp.status_code == 200
    assert resp.json()["valid"] is True
    assert ms < SLA["verify_hit"], f"GET /verify/hit: {ms:.1f}ms > SLA {SLA['verify_hit']}ms"