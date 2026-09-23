"""
Fitness Function: Modularidade e coesão.

Valida que o sistema mantém responsabilidades bem definidas e que componentes
podem evoluir de forma independente.
"""

import ast
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent / "src"

EXPECTED_MODULES = ["models", "repositories", "services", "api", "infrastructure"]
MAX_LINES_PER_FILE = 200


def count_code_lines(filepath: Path) -> int:
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
    return len([l for l in lines if l.strip() and not l.strip().startswith("#")])


def test_all_architectural_modules_exist():
    """Todos os módulos arquiteturais definidos na arquitetura devem existir."""
    for module in EXPECTED_MODULES:
        module_dir = SRC_DIR / module
        assert module_dir.is_dir(), (
            f"Módulo arquitetural '{module}' não encontrado em src/. "
            f"Estrutura de camadas foi alterada sem atualizar este teste."
        )


def test_file_size_budget():
    """
    Nenhum arquivo deve ultrapassar MAX_LINES_PER_FILE linhas de código.
    Arquivos grandes indicam violação de Responsabilidade Única.
    """
    for py_file in SRC_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        lines = count_code_lines(py_file)
        assert lines <= MAX_LINES_PER_FILE, (
            f"{py_file.relative_to(SRC_DIR)} tem {lines} linhas "
            f"(máximo: {MAX_LINES_PER_FILE}). "
            f"Divida em módulos menores para manter coesão."
        )


def test_ai_provider_uses_factory():
    """
    AIService deve expor get_ai_provider() como factory.
    Garante que providers são injetáveis e substituíveis (ADR-002).
    """
    ai_file = SRC_DIR / "services" / "ai_service.py"
    assert ai_file.exists(), "src/services/ai_service.py não encontrado"

    with open(ai_file, encoding="utf-8") as f:
        content = f.read()

    assert "get_ai_provider" in content, (
        "ai_service.py deve expor get_ai_provider() como factory. "
        "Services e routes obtêm o provider através desta função."
    )
    assert "Protocol" in content, (
        "AIProvider deve ser definido como Protocol para garantir substituibilidade."
    )


def test_repository_contract_coverage():
    """
    Todos os repositories concretos devem implementar ou herdar get_by_id, create, list.
    Garante que services podem trocar de repository sem adaptação.
    """
    repos_dir = SRC_DIR / "repositories"
    required_methods = ["get_by_id", "create", "list"]

    for py_file in repos_dir.glob("*.py"):
        if py_file.name in ("__init__.py",):
            continue
        with open(py_file, encoding="utf-8") as f:
            content = f.read()

        if "BaseRepository" in content:
            # Herda o contrato — não precisa redefinir todos os métodos
            continue

        missing = [m for m in required_methods if m not in content]
        assert not missing, (
            f"{py_file.name} não implementa {missing} e não herda de BaseRepository. "
            f"Siga o contrato definido em repositories/base.py."
        )


def test_config_is_single_source_of_truth():
    """
    Valores de configuração devem vir de settings — não hardcoded nos módulos.
    Garante que mudanças de ambiente não exigem alteração de código.
    """
    forbidden = [
        'host="localhost"',
        "host='localhost'",
        "port=5432",
        "port=3306",
        'database="postgres"',
    ]
    for py_file in SRC_DIR.rglob("*.py"):
        if py_file.name == "config.py":
            continue
        with open(py_file, encoding="utf-8") as f:
            content = f.read()
        for pattern in forbidden:
            assert pattern not in content, (
                f"{py_file.name} contém configuração hardcoded: '{pattern}'. "
                f"Use src/config.py como fonte única de verdade."
            )