"""
FITNESS FUNCTION: Evolvabilidade e Modularidade.

Verifica que a arquitetura suporta mudança incremental:
- Número de módulos src/ não excede limite (força decomposição)
- Domain não cresce acoplado a frameworks
- Existência de seams de evolução (repositórios, services)
- Versioning de API presente
"""

import ast
from pathlib import Path

import pytest


MAX_DOMAIN_CLASSES = 20
MAX_SERVICE_DEPENDENCIES = 4


def test_api_is_versioned():
    """Fitness: API deve ter versionamento para evolução sem quebrar contratos."""
    api_path = Path("src/api/v1")
    assert api_path.exists(), (
        "API deve estar sob src/api/v1/ — versionamento é obrigatório para "
        "evolução incremental sem quebrar clientes existentes"
    )
    router_file = api_path / "router.py"
    assert router_file.exists(), "src/api/v1/router.py deve existir"


def test_domain_does_not_exceed_complexity_limit():
    """Fitness: domínio não deve crescer além do limite de classes."""
    domain_path = Path("src/domain")
    class_count = 0
    for py_file in domain_path.rglob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
        class_count += sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    assert class_count <= MAX_DOMAIN_CLASSES, (
        f"Domínio tem {class_count} classes (máx={MAX_DOMAIN_CLASSES}). "
        "Considere dividir em bounded contexts separados."
    )


def test_services_have_repository_seam():
    """Fitness: serviços devem receber repositórios via injeção (seam de evolução)."""
    service_files = list(Path("src/services").rglob("*.py"))
    violations = []
    for py_file in service_files:
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "Service" in node.name:
                init_methods = [
                    n for n in ast.walk(node)
                    if isinstance(n, ast.FunctionDef) and n.name == "__init__"
                ]
                if not init_methods:
                    violations.append(
                        f"{py_file} — '{node.name}' sem __init__ (sem injeção de dependência)"
                    )
    assert not violations, (
        "Serviços sem injeção de dependência perdem o seam de evolução:\n"
        + "\n".join(violations)
    )


def test_schemas_separated_from_domain():
    """Fitness: schemas de API não devem estar misturados com modelos de domínio."""
    domain_files = list(Path("src/domain").rglob("*.py"))
    for py_file in domain_files:
        source = py_file.read_text(encoding="utf-8")
        assert "BaseModel" not in source, (
            f"{py_file}: modelos Pydantic (BaseModel) não devem estar no domínio. "
            "Use src/api/v1/schemas.py para contratos de API."
        )


def test_repository_pattern_present():
    """Fitness: camada de repositório deve existir como seam de persistência."""
    repo_file = Path("src/infrastructure/repositories.py")
    assert repo_file.exists(), (
        "src/infrastructure/repositories.py deve existir — "
        "é o seam que permite trocar a persistência sem afetar o domínio"
    )
    source = repo_file.read_text(encoding="utf-8")
    assert "Repository" in source, (
        "repositories.py deve conter classes de repositório"
    )