"""
FITNESS FUNCTION: Imutabilidade do Audit Trail.

Verifica que o repositório de auditoria nunca expõe métodos de deleção
ou atualização de registros — exigência crítica para compliance regulatório
(LGPD Art. 37, SOX Section 802, PCI DSS Requirement 10.5).
"""

import ast
import inspect
from pathlib import Path

import pytest

from src.infrastructure.repositories import AuditRepository


def test_audit_repository_has_no_delete_method():
    """Fitness: AuditRepository não pode ter método delete/remove/truncate."""
    forbidden_names = {"delete", "remove", "truncate", "clear", "drop", "purge"}
    methods = {
        name for name, _ in inspect.getmembers(AuditRepository, predicate=inspect.isfunction)
    }
    violations = forbidden_names & methods
    assert not violations, (
        f"AuditRepository expõe métodos de deleção: {violations}. "
        "Audit trail deve ser append-only para conformidade regulatória."
    )


def test_audit_repository_has_no_update_method():
    """Fitness: AuditRepository não pode ter método de atualização."""
    forbidden_names = {"update", "edit", "modify", "patch"}
    methods = {
        name for name, _ in inspect.getmembers(AuditRepository, predicate=inspect.isfunction)
    }
    violations = forbidden_names & methods
    assert not violations, (
        f"AuditRepository expõe métodos de atualização: {violations}. "
        "Eventos de auditoria são imutáveis por design."
    )


def test_audit_orm_table_has_no_cascade_delete():
    """Fitness: tabela audit_events não deve ter cascade delete no ORM."""
    orm_file = Path("src/infrastructure/orm_models.py")
    source = orm_file.read_text(encoding="utf-8")
    assert "audit_events" in source, "Tabela audit_events deve existir"
    audit_section_start = source.index("audit_events")
    audit_section = source[audit_section_start : audit_section_start + 500]
    assert "cascade" not in audit_section.lower(), (
        "Tabela audit_events não pode ter CASCADE DELETE"
    )


def test_audit_record_method_exists():
    """Fitness: AuditRepository deve expor método record() para append."""
    assert hasattr(AuditRepository, "record"), (
        "AuditRepository precisa do método record() para garantir append-only"
    )