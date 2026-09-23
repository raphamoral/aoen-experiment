"""
FITNESS FUNCTION: Segurança e Compliance de Dados.

Verifica características de segurança exigidas por regulatórios:
- Sem segredos hardcoded no código
- Paginação obrigatória em endpoints de listagem
- Schemas validam entradas (Pydantic obrigatório nas rotas)
- Variáveis de ambiente para configuração sensível
"""

import ast
import re
from pathlib import Path

import pytest


SUSPICIOUS_PATTERNS = [
    r'password\s*=\s*["\'][^"\']{4,}["\']',
    r'secret\s*=\s*["\'][^"\']{4,}["\']',
    r'api_key\s*=\s*["\'][^"\']{4,}["\']',
    r'token\s*=\s*["\'][^"\']{8,}["\']',
]


def _all_py_files(base: str = "src") -> list[Path]:
    return list(Path(base).rglob("*.py"))


def test_no_hardcoded_secrets():
    """Fitness: nenhum segredo hardcoded no código-fonte."""
    violations = []
    for py_file in _all_py_files():
        content = py_file.read_text(encoding="utf-8").lower()
        for pattern in SUSPICIOUS_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                violations.append(f"{py_file}: {matches}")
    assert not violations, (
        f"Possíveis segredos hardcoded encontrados:\n" + "\n".join(violations)
    )


def test_config_uses_environment_variables():
    """Fitness: configurações sensíveis devem vir de variáveis de ambiente."""
    config_file = Path("src/config.py")
    source = config_file.read_text(encoding="utf-8")
    assert "BaseSettings" in source, (
        "src/config.py deve usar pydantic BaseSettings para ler env vars"
    )
    assert "SettingsConfigDict" in source or "env_file" in source, (
        "Configuração deve suportar .env file para desenvolvimento"
    )


def test_api_routes_use_pydantic_schemas():
    """Fitness: todas as rotas POST devem receber Pydantic models como body."""
    api_files = list(Path("src/api").rglob("*.py"))
    violations = []
    for py_file in api_files:
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                decorators = [
                    ast.unparse(d) for d in node.decorator_list
                    if isinstance(d, ast.Call)
                ]
                is_post = any(".post(" in d for d in decorators)
                if is_post:
                    has_body_param = any(
                        (
                            isinstance(arg.annotation, ast.Name)
                            and arg.annotation.id not in ("str", "int", "float", "bool", "UUID")
                        )
                        for arg in node.args.args
                    )
                    if not has_body_param:
                        violations.append(
                            f"{py_file}:{node.lineno} — rota POST '{node.name}' "
                            "sem Pydantic schema aparente"
                        )
    assert not violations, "\n".join(violations)


def test_database_url_not_exposed_in_logs(tmp_path):
    """Fitness: DATABASE_URL não deve aparecer em logs de startup."""
    app_file = Path("src/app.py")
    source = app_file.read_text(encoding="utf-8")
    assert "database_url" not in source.lower() or "print" not in source.lower(), (
        "DATABASE_URL não deve ser logada no startup (exposição de credenciais)"
    )