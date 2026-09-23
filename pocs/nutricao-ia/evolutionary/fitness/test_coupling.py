"""
Fitness Function: Acoplamento entre camadas.

Valida que as dependências seguem a direção única permitida:
    api → services → repositories → models
                 ↑
         infrastructure (apenas de repositories/services)

Falha aqui = build quebrado. Corrija a importação, não o teste.
"""

import ast
from pathlib import Path

SRC_DIR = Path(__file__).parent.parent / "src"

# Wiring layer tem acoplamento intencional — não verificar acoplamento nele.
COUPLING_EXEMPT = {"dependencies.py"}


def get_internal_imports(filepath: Path) -> list[str]:
    """Retorna todos os imports de módulos src.* encontrados no arquivo."""
    with open(filepath, encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return []

    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("src."):
                    imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("src."):
                imports.append(node.module)
    return imports


def test_models_do_not_import_upper_layers():
    """Models são a camada mais interna: nunca importam services, repositories ou api."""
    models_dir = SRC_DIR / "models"
    for py_file in models_dir.glob("*.py"):
        imports = get_internal_imports(py_file)
        violations = [
            i for i in imports if any(layer in i for layer in ("services", "repositories", "api"))
        ]
        assert not violations, (
            f"VIOLAÇÃO DE ACOPLAMENTO em models/{py_file.name}: "
            f"importa camadas superiores {violations}. "
            f"Models devem depender apenas de src.models.base."
        )


def test_repositories_do_not_import_services_or_api():
    """Repositories acessam apenas models e infrastructure — nunca services ou api."""
    repos_dir = SRC_DIR / "repositories"
    for py_file in repos_dir.glob("*.py"):
        imports = get_internal_imports(py_file)
        violations = [i for i in imports if "services" in i or "src.api" in i]
        assert not violations, (
            f"VIOLAÇÃO DE ACOPLAMENTO em repositories/{py_file.name}: "
            f"importa camadas superiores {violations}."
        )


def test_services_do_not_import_api():
    """Services implementam lógica de negócio sem conhecer a camada HTTP."""
    services_dir = SRC_DIR / "services"
    for py_file in services_dir.glob("*.py"):
        imports = get_internal_imports(py_file)
        violations = [i for i in imports if "src.api" in i]
        assert not violations, (
            f"VIOLAÇÃO DE ACOPLAMENTO em services/{py_file.name}: "
            f"importa camada de API {violations}. "
            f"Services não devem conhecer detalhes HTTP."
        )


def test_routes_do_not_import_repositories_directly():
    """Routes delegam acesso a dados para services — nunca acessam repositories diretamente."""
    routes_dir = SRC_DIR / "api" / "routes"
    for py_file in routes_dir.glob("*.py"):
        imports = get_internal_imports(py_file)
        violations = [i for i in imports if "repositories" in i]
        assert not violations, (
            f"VIOLAÇÃO DE ACOPLAMENTO em routes/{py_file.name}: "
            f"acessa repositories diretamente {violations}. "
            f"Use services como intermediário."
        )


def test_coupling_budget_per_module():
    """
    Nenhum módulo deve depender de mais de MAX_MODULE_COUPLING módulos internos.
    Budget alto para wiring layer (dependencies.py) — excluído desta verificação.
    """
    from src.config import settings

    for py_file in SRC_DIR.rglob("*.py"):
        if py_file.name in ("__init__.py", *COUPLING_EXEMPT):
            continue
        imports = get_internal_imports(py_file)
        unique_top_modules = {i.split(".")[1] for i in imports}  # src.<module>.*
        assert len(unique_top_modules) <= settings.MAX_MODULE_COUPLING, (
            f"{py_file.relative_to(SRC_DIR)} excede budget de acoplamento: "
            f"{len(unique_top_modules)}/{settings.MAX_MODULE_COUPLING} módulos "
            f"({unique_top_modules}). Refatore para reduzir dependências."
        )