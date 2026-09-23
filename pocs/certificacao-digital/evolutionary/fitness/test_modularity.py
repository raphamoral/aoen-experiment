"""
Fitness Function: Dependency Direction
───────────────────────────────────────
Protege a direção correta de dependências entre camadas:

    API  →  Services  →  Domain  ←  Infrastructure

Regras:
  - Domain NUNCA importa de API ou Services
  - Infrastructure NUNCA importa de API ou Services
  - Services NUNCA importa de API

Violar qualquer regra indica que uma abstração está faltando
ou que responsabilidades estão no lugar errado.
"""

import ast
from pathlib import Path


def _get_imports(filepath: Path) -> list[str]:
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    result: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.append(node.module)
    return result


def _violations_for(layer_path: Path, forbidden_prefixes: list[str]) -> list[str]:
    violations: list[str] = []
    for py_file in layer_path.rglob("*.py"):
        imports = _get_imports(py_file)
        bad = [i for i in imports if any(i.startswith(p) for p in forbidden_prefixes)]
        if bad:
            violations.append(f"  {py_file} → {bad}")
    return violations


def test_domain_does_not_import_api():
    v = _violations_for(Path("src/domain"), ["src.api"])
    assert not v, "Domain importando de API (inversão proibida):\n" + "\n".join(v)


def test_domain_does_not_import_services():
    v = _violations_for(Path("src/domain"), ["src.services"])
    assert not v, "Domain importando de Services:\n" + "\n".join(v)


def test_infrastructure_does_not_import_api():
    v = _violations_for(Path("src/infrastructure"), ["src.api"])
    assert not v, "Infrastructure importando de API:\n" + "\n".join(v)


def test_infrastructure_does_not_import_services():
    v = _violations_for(Path("src/infrastructure"), ["src.services"])
    assert not v, "Infrastructure importando de Services:\n" + "\n".join(v)


def test_services_does_not_import_api():
    v = _violations_for(Path("src/services"), ["src.api"])
    assert not v, "Services importando de API:\n" + "\n".join(v)