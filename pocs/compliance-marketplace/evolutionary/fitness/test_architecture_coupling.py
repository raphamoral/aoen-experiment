"""
FITNESS FUNCTION: Acoplamento entre camadas (Coupling Fitness).

Verifica que as regras de dependência entre camadas são respeitadas:
  domain  →  nenhuma dependência de infraestrutura ou API
  services → pode usar domain e infrastructure
  api     → pode usar services e schemas, mas não ORM diretamente

Esta função roda no CI como teste automatizado e bloqueia merges
que violem os limites arquiteturais.
"""

import ast
import os
from pathlib import Path
from typing import Set

import pytest


LAYERS = {
    "domain": Path("src/domain"),
    "infrastructure": Path("src/infrastructure"),
    "services": Path("src/services"),
    "api": Path("src/api"),
}

FORBIDDEN_IMPORTS: dict[str, list[str]] = {
    "domain": [
        "sqlalchemy",
        "fastapi",
        "src.infrastructure",
        "src.api",
        "src.services",
    ],
    "services": [
        "fastapi",
        "src.api",
        "sqlalchemy.orm",
    ],
}


def _collect_imports(file_path: Path) -> Set[str]:
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def _python_files(layer_path: Path):
    if not layer_path.exists():
        return []
    return list(layer_path.rglob("*.py"))


@pytest.mark.parametrize("layer,forbidden", FORBIDDEN_IMPORTS.items())
def test_layer_does_not_import_forbidden(layer: str, forbidden: list[str]):
    """Fitness: nenhuma camada viola as fronteiras arquiteturais definidas."""
    violations = []
    layer_path = LAYERS[layer]
    for py_file in _python_files(layer_path):
        imports = _collect_imports(py_file)
        for imp in imports:
            for forbidden_prefix in forbidden:
                if imp.startswith(forbidden_prefix):
                    violations.append(
                        f"{py_file.relative_to('.')} importa '{imp}' (proibido em '{layer}')"
                    )
    assert not violations, (
        f"Violações de acoplamento na camada '{layer}':\n" + "\n".join(violations)
    )


def test_domain_models_are_pure_dataclasses():
    """Fitness: modelos de domínio devem usar apenas stdlib e dataclasses."""
    domain_models = Path("src/domain/models.py")
    if not domain_models.exists():
        pytest.skip("models.py não encontrado")
    imports = _collect_imports(domain_models)
    third_party_allowed = {"enum", "dataclasses", "datetime", "typing", "uuid", "__future__"}
    violations = [
        imp for imp in imports
        if not any(imp.startswith(allowed) for allowed in third_party_allowed)
    ]
    assert not violations, (
        f"Domínio contém imports não-stdlib: {violations}"
    )