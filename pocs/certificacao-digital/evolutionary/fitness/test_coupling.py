"""
Fitness Function: Bounded Module Coupling
─────────────────────────────────────────
Protege: crescimento orgânico do sistema não deve criar módulos
         com acoplamento excessivo a outros módulos internos.

Threshold: nenhum arquivo em src/ pode importar mais de
           MAX_INTERNAL_IMPORTS módulos src/ distintos.

Ao atingir o limite, o sinal é refatorar (extrair serviço/interface),
não aumentar o threshold.
"""

import ast
from pathlib import Path

MAX_INTERNAL_IMPORTS = 5


def _get_internal_imports(filepath: Path) -> list[str]:
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names if a.name.startswith("src."))
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("src."):
                imports.append(node.module)
    return imports


def test_bounded_coupling():
    """Cada módulo src/ deve depender de no máximo MAX_INTERNAL_IMPORTS outros."""
    violations: list[str] = []

    for py_file in Path("src").rglob("*.py"):
        unique_deps = set(_get_internal_imports(py_file))
        if len(unique_deps) > MAX_INTERNAL_IMPORTS:
            violations.append(
                f"  {py_file}: {len(unique_deps)} dependências internas "
                f"(máximo permitido: {MAX_INTERNAL_IMPORTS})\n"
                f"    deps: {sorted(unique_deps)}"
            )

    assert not violations, (
        f"Violações de acoplamento detectadas ({len(violations)}):\n" + "\n".join(violations)
    )


def test_no_direct_circular_imports():
    """Detecta ciclos diretos A→B e B→A entre módulos src/."""
    graph: dict[str, set[str]] = {}

    for py_file in Path("src").rglob("*.py"):
        key = py_file.as_posix().removesuffix(".py").replace("/", ".")
        graph[key] = set(_get_internal_imports(py_file))

    cycles: list[str] = []
    for module, deps in graph.items():
        for dep in deps:
            if module in graph.get(dep, set()):
                pair = tuple(sorted([module, dep]))
                label = f"  {pair[0]} <-> {pair[1]}"
                if label not in cycles:
                    cycles.append(label)

    assert not cycles, "Ciclos de importação diretos detectados:\n" + "\n".join(cycles)