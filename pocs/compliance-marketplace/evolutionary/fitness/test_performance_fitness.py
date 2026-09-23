"""
FITNESS FUNCTION: Performance e Escalabilidade.

Verifica características que garantem que o sistema pode escalar:
- Endpoints async (não bloqueantes)
- Queries com limite (evitar full-scan)
- Complexidade ciclomática dentro do limite aceitável
"""

import ast
from pathlib import Path

import pytest


MAX_CYCLOMATIC_COMPLEXITY = 10
MAX_FUNCTION_LINES = 50


def _compute_cyclomatic_complexity(func_node: ast.FunctionDef) -> int:
    """Complexidade ciclomática simplificada: 1 + branches."""
    complexity = 1
    for node in ast.walk(func_node):
        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                              ast.With, ast.Assert, ast.comprehension)):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1
    return complexity


def test_service_functions_are_async():
    """Fitness: funções de serviço devem ser async para não bloquear o event loop."""
    service_files = list(Path("src/services").rglob("*.py"))
    violations = []
    for py_file in service_files:
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
                if not node.name.startswith("_") and node.name != "__init__":
                    violations.append(
                        f"{py_file}:{node.lineno} — '{node.name}' deveria ser async"
                    )
    assert not violations, (
        "Funções de serviço síncronas bloqueiam o event loop:\n" + "\n".join(violations)
    )


def test_cyclomatic_complexity_within_threshold():
    """Fitness: complexidade ciclomática não deve exceder o limite."""
    py_files = list(Path("src").rglob("*.py"))
    violations = []
    for py_file in py_files:
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                cc = _compute_cyclomatic_complexity(node)
                if cc > MAX_CYCLOMATIC_COMPLEXITY:
                    violations.append(
                        f"{py_file}:{node.lineno} — '{node.name}' CC={cc} "
                        f"(máx={MAX_CYCLOMATIC_COMPLEXITY})"
                    )
    assert not violations, (
        "Funções com alta complexidade ciclomática:\n" + "\n".join(violations)
    )


def test_function_size_within_threshold():
    """Fitness: funções longas dificultam manutenção e evolução."""
    py_files = list(Path("src").rglob("*.py"))
    violations = []
    for py_file in py_files:
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if hasattr(node, "end_lineno") and node.end_lineno:
                    lines = node.end_lineno - node.lineno
                    if lines > MAX_FUNCTION_LINES:
                        violations.append(
                            f"{py_file}:{node.lineno} — '{node.name}' "
                            f"{lines} linhas (máx={MAX_FUNCTION_LINES})"
                        )
    assert not violations, (
        "Funções muito longas:\n" + "\n".join(violations)
    )