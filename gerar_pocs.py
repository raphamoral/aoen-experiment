# -*- coding: utf-8 -*-
"""Gera 3 repositórios POC: 3 ideias x 7 abordagens em paralelo."""
import subprocess
import os
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

POC_DIR = Path("pocs")

IDEIAS = {
    "compliance-marketplace": "Marketplace de freelancers especializados em compliance regulatório",
    "nutricao-ia": "App de nutrição personalizada com IA baseada em exames laboratoriais",
    "certificacao-digital": "Plataforma de certificação digital de cursos livres com verificação pública",
}

ABORDAGENS = {
    "aoen": """Você é um desenvolvedor senior que segue o framework AOEN para construir projetos.

AOEN - 4 fases:
1. NÚCLEO (VALOR): Identificar core diferenciador, construir com Service Layer desacoplada
2. MULTI-INTERFACE (ALCANCE): Múltiplas interfaces sobre mesma lógica, cada uma abre um mercado
3. CONFIG-DRIVEN (ESCALA): Fluxo fixo no código, parâmetros configuráveis por cliente
4. ISOLAMENTO (CUSTO): Core isolado em processo separado, custo mensurável por cliente

Princípio: toda decisão preserva a capacidade de evoluir.

Gere um projeto Python (FastAPI) com:
- main.py (FastAPI app)
- models.py (SQLAlchemy models)
- services/ (Service Layer desacoplada)
- routers/ (endpoints finos)
- config.py (configuração por tenant)
- core/ (núcleo diferenciador isolado)
- requirements.txt
- README.md explicando decisões AOEN""",

    "clean-arch": """Você é um desenvolvedor senior que segue estritamente Clean Architecture de Robert C. Martin.

Regras:
- 4 camadas: Entities, Use Cases, Interface Adapters, Frameworks & Drivers
- Dependências só apontam para dentro
- Independente de framework, UI e banco

Gere um projeto Python (FastAPI) com:
- entities/ (regras de negócio)
- use_cases/ (casos de uso)
- adapters/ (interface adapters)
- frameworks/ (drivers e infra)
- main.py
- requirements.txt
- README.md explicando decisões Clean Architecture""",

    "hexagonal": """Você é um desenvolvedor senior que segue estritamente Hexagonal Architecture de Alistair Cockburn.

Regras:
- Separação inside (domínio) e outside (infra)
- Ports são interfaces abstratas
- Adapters conectam ao mundo externo
- Tratamento simétrico de todos sistemas externos

Gere um projeto Python (FastAPI) com:
- domain/ (lógica de negócio)
- ports/ (interfaces abstratas)
- adapters/ (implementações concretas)
- main.py
- requirements.txt
- README.md explicando decisões Hexagonal""",

    "12factor": """Você é um desenvolvedor senior que segue estritamente The Twelve-Factor App.

Regras:
- Config no ambiente (env vars)
- Processos stateless
- Serviços de apoio como recursos
- Concorrência via processos
- Dev/prod parity

Gere um projeto Python (FastAPI) com:
- app/ (aplicação stateless)
- Procfile (processo model)
- .env.example
- main.py
- requirements.txt
- README.md explicando decisões 12-Factor""",

    "evolutionary": """Você é um desenvolvedor senior que segue Evolutionary Architecture de Neal Ford.

Regras:
- Fitness functions para validar características
- Decisões reversíveis quando possível
- Mudança incremental guiada
- Last responsible moment

Gere um projeto Python (FastAPI) com:
- src/ (código principal)
- fitness/ (fitness functions/testes arquiteturais)
- main.py
- requirements.txt
- README.md explicando decisões Evolutionary Architecture""",

    "arch-flow": """Você é um desenvolvedor senior que segue Architecture for Flow de Susanne Kaiser (DDD + Wardley Mapping + Team Topologies).

Regras:
- Bounded contexts por domínio
- Componentes classificados por maturidade (genesis/custom/product/commodity)
- Organização por fluxo de valor
- Linguagem ubíqua

Gere um projeto Python (FastAPI) com:
- contexts/ (bounded contexts separados)
- shared/ (kernel compartilhado)
- main.py
- requirements.txt
- README.md explicando decisões Architecture for Flow""",

    "sem-framework": """Você é um desenvolvedor que vai construir um produto. Você NÃO pode usar nenhum padrão de arquitetura. Nada de Clean Architecture, Hexagonal, MVC, Service Layer, camadas, DDD, microserviços. Pense de forma intuitiva e direta. Coloque tudo junto da forma mais simples.

Gere um projeto Python com:
- app.py (tudo junto - rotas, lógica, banco)
- requirements.txt
- README.md""",
}

PROMPT_TEMPLATE = """{instrucoes}

PRODUTO: "{ideia}"

FORMATO: para cada arquivo use exatamente:
===FILE: caminho/do/arquivo.py===
conteúdo do arquivo
===END===

Gere APENAS os blocos de arquivo, sem texto adicional fora deles."""


def run_claude(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", "sonnet"],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return result.stdout.strip() if result.returncode == 0 else f"ERROR: {result.stderr}"
    except Exception as e:
        return f"ERROR: {str(e)}"


def parse_files(response: str) -> dict:
    files = {}
    parts = response.split("===FILE: ")
    for part in parts[1:]:
        if "===END===" in part:
            header, rest = part.split("===", 1)
            filepath = header.strip().rstrip("=").strip()
            content = rest.split("===END===")[0].strip()
            if content.startswith("```"):
                first_nl = content.find("\n")
                content = content[first_nl + 1:]
            if content.endswith("```"):
                content = content[:-3].strip()
            files[filepath] = content
    return files


def generate_one(slug, ideia, ab_name, instrucoes):
    """Gera uma POC (1 ideia x 1 abordagem)."""
    ab_dir = POC_DIR / slug / ab_name

    # Skip se já tem arquivos reais (não só _raw)
    if ab_dir.exists():
        real_files = [f for f in ab_dir.iterdir() if f.is_file() and f.name != "_raw_response.txt"]
        if real_files:
            return (slug, ab_name, "SKIP", len(real_files))

    prompt = PROMPT_TEMPLATE.format(instrucoes=instrucoes, ideia=ideia)
    response = run_claude(prompt)

    if response.startswith("ERROR"):
        return (slug, ab_name, "ERROR", response[:80])

    files = parse_files(response)
    if not files:
        ab_dir.mkdir(parents=True, exist_ok=True)
        with open(ab_dir / "_raw_response.txt", "w", encoding="utf-8") as f:
            f.write(response)
        return (slug, ab_name, "PARSE_FAIL", len(response))

    ab_dir.mkdir(parents=True, exist_ok=True)
    for filepath, content in files.items():
        full_path = ab_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    return (slug, ab_name, "OK", len(files))


def main():
    POC_DIR.mkdir(exist_ok=True)

    # Montar todas as tarefas
    tasks = []
    for slug, ideia in IDEIAS.items():
        for ab_name, instrucoes in ABORDAGENS.items():
            tasks.append((slug, ideia, ab_name, instrucoes))

    total = len(tasks)
    done = 0

    print(f"\n{'=' * 60}")
    print(f"GERANDO {total} POCs (3 repos x 7 abordagens) — 7 em paralelo")
    print(f"{'=' * 60}\n")

    # Rodar tudo em paralelo (7 workers)
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = {}
        for slug, ideia, ab_name, instrucoes in tasks:
            f = executor.submit(generate_one, slug, ideia, ab_name, instrucoes)
            futures[f] = (slug, ab_name)

        for future in as_completed(futures):
            slug, ab_name = futures[future]
            done += 1
            try:
                result = future.result()
                _, _, status, detail = result
                print(f"  [{done:2d}/{total}] {slug}/{ab_name}: {status} ({detail})")
            except Exception as e:
                print(f"  [{done:2d}/{total}] {slug}/{ab_name}: EXCEPTION ({e})")

    # Git init pra cada repo
    for slug in IDEIAS:
        repo_dir = POC_DIR / slug
        if not (repo_dir / ".git").exists():
            subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True)
            subprocess.run(["git", "add", "."], cwd=str(repo_dir), capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", f"POC: {IDEIAS[slug]}"],
                cwd=str(repo_dir), capture_output=True,
                env={**os.environ,
                     "GIT_AUTHOR_NAME": "AOEN Experiment",
                     "GIT_AUTHOR_EMAIL": "experiment@aoen.dev",
                     "GIT_COMMITTER_NAME": "AOEN Experiment",
                     "GIT_COMMITTER_EMAIL": "experiment@aoen.dev"})

    # Resumo
    print(f"\n{'=' * 60}")
    print("RESUMO:")
    print(f"{'=' * 60}")
    for repo in sorted(POC_DIR.iterdir()):
        if repo.is_dir() and not repo.name.startswith('.'):
            print(f"\n  {repo.name}/")
            for ab in sorted(repo.iterdir()):
                if ab.is_dir() and not ab.name.startswith('.'):
                    files = [f for f in ab.rglob("*") if f.is_file() and '.git' not in str(f) and f.name != "_raw_response.txt"]
                    print(f"    {ab.name}/  ({len(files)} arquivos)")


if __name__ == "__main__":
    main()
