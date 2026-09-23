# -*- coding: utf-8 -*-
"""Executa o experimento AOEN: 100 ideias x 7 abordagens via claude CLI."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

EXPERIMENT_DIR = Path("experimento")
RESULTS_DIR = EXPERIMENT_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

with open(EXPERIMENT_DIR / "ideias.json", "r", encoding="utf-8") as f:
    IDEIAS = json.load(f)

# Import prompts
sys.path.insert(0, ".")
from experimento_aoen import ABORDAGENS, PROMPT_AVALIADOR


def run_claude(prompt: str, timeout: int = 120) -> str:
    """Executa prompt via claude CLI e retorna a resposta."""
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", "sonnet"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8"
        )
        return result.stdout.strip() if result.returncode == 0 else f"ERROR: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "ERROR: timeout"
    except Exception as e:
        return f"ERROR: {str(e)}"


def extract_json(text: str) -> dict:
    """Tenta extrair JSON de uma resposta que pode ter texto ao redor."""
    # Tenta parse direto
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Tenta encontrar JSON no texto
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return {"raw_response": text}


def run_single(ideia_idx: int, ideia: str, abordagem: str, prompt_template: str) -> dict:
    """Executa uma única combinação ideia x abordagem."""
    result_file = RESULTS_DIR / f"idea_{ideia_idx:03d}_{abordagem}.json"

    # Skip se já existe
    if result_file.exists():
        with open(result_file, "r", encoding="utf-8") as f:
            return json.load(f)

    prompt = prompt_template.format(ideia=ideia)
    response = run_claude(prompt)
    parsed = extract_json(response)

    result = {
        "ideia_idx": ideia_idx,
        "ideia": ideia,
        "abordagem": abordagem,
        "response": parsed,
        "raw": response[:2000]  # truncar raw pra não ficar enorme
    }

    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def evaluate_single(ideia_idx: int, ideia: str, abordagem: str, response: dict) -> dict:
    """Avalia uma resposta com o avaliador IA."""
    eval_file = RESULTS_DIR / f"eval_{ideia_idx:03d}_{abordagem}.json"

    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            return json.load(f)

    prompt = PROMPT_AVALIADOR.format(
        ideia=ideia,
        abordagem=abordagem,
        resposta=json.dumps(response, ensure_ascii=False, indent=2)[:3000]
    )
    raw = run_claude(prompt)
    parsed = extract_json(raw)

    result = {
        "ideia_idx": ideia_idx,
        "abordagem": abordagem,
        "scores": parsed
    }

    with open(eval_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def run_batch(start: int = 0, end: int = None, max_workers: int = 5):
    """Executa um lote de ideias."""
    if end is None:
        end = len(IDEIAS)

    total = (end - start) * len(ABORDAGENS)
    done = 0

    print(f"\n{'='*60}")
    print(f"EXPERIMENTO AOEN — Ideias {start}-{end-1} ({end-start} ideias x {len(ABORDAGENS)} abordagens = {total} execuções)")
    print(f"{'='*60}\n")

    for i in range(start, end):
        ideia = IDEIAS[i]
        print(f"\n[Ideia {i+1}/{end}] {ideia[:60]}...")

        # Executar as 7 abordagens pra essa ideia
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for abordagem, prompt_template in ABORDAGENS.items():
                f = executor.submit(run_single, i, ideia, abordagem, prompt_template)
                futures[f] = abordagem

            for future in as_completed(futures):
                abordagem = futures[future]
                try:
                    result = future.result()
                    done += 1
                    has_json = "raw_response" not in result.get("response", {})
                    status = "OK" if has_json else "RAW"
                    print(f"  [{done}/{total}] {abordagem}: {status}")
                except Exception as e:
                    done += 1
                    print(f"  [{done}/{total}] {abordagem}: ERROR - {e}")

        # Avaliar as respostas dessa ideia
        print(f"  Avaliando...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            eval_futures = {}
            for abordagem in ABORDAGENS:
                result_file = RESULTS_DIR / f"idea_{i:03d}_{abordagem}.json"
                if result_file.exists():
                    with open(result_file, "r", encoding="utf-8") as f:
                        result = json.load(f)
                    ef = executor.submit(evaluate_single, i, ideia, abordagem, result["response"])
                    eval_futures[ef] = abordagem

            for future in as_completed(eval_futures):
                abordagem = eval_futures[future]
                try:
                    future.result()
                    print(f"  eval_{abordagem}: OK")
                except Exception as e:
                    print(f"  eval_{abordagem}: ERROR - {e}")

    print(f"\n{'='*60}")
    print(f"COMPLETO: {done} execuções + avaliações")
    print(f"{'='*60}")


def consolidate():
    """Consolida todos os resultados em um único arquivo."""
    all_evals = []
    for f in sorted(RESULTS_DIR.glob("eval_*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            all_evals.append(json.load(fh))

    with open(EXPERIMENT_DIR / "consolidated.json", "w", encoding="utf-8") as f:
        json.dump(all_evals, f, ensure_ascii=False, indent=2)

    print(f"Consolidado: {len(all_evals)} avaliações em experimento/consolidated.json")
    return all_evals


def generate_charts():
    """Gera gráficos comparativos."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    with open(EXPERIMENT_DIR / "consolidated.json", "r", encoding="utf-8") as f:
        evals = json.load(f)

    criterios = [
        "core_diferenciador", "visao_mercado", "multi_interface",
        "configurabilidade", "isolamento_processamento",
        "consideracao_custo", "monetizacao", "evolucao", "coerencia"
    ]

    criterios_labels = [
        "Core\nDiferenciador", "Visão de\nMercado", "Multi-\nInterface",
        "Configura-\nbilidade", "Isolamento\nProcess.", "Consideração\nde Custo",
        "Moneti-\nzação", "Evolução", "Coerência"
    ]

    abordagens = ["aoen", "clean_arch", "hexagonal", "12factor",
                   "evolutionary", "arch_flow", "sem_framework"]
    abordagens_labels = ["AOEN", "Clean\nArch", "Hexa-\ngonal", "12-\nFactor",
                          "Evolu-\ntionary", "Arch\nFlow", "Sem\nFramework"]

    # Calcular médias por abordagem x critério
    scores = {a: {c: [] for c in criterios} for a in abordagens}

    for ev in evals:
        ab = ev["abordagem"]
        sc = ev.get("scores", {})
        if "raw_response" in sc:
            continue
        for c in criterios:
            val = sc.get(c)
            if isinstance(val, (int, float)):
                scores[ab][c].append(val)

    # Médias
    means = {}
    for a in abordagens:
        means[a] = {}
        for c in criterios:
            vals = scores[a][c]
            means[a][c] = sum(vals) / len(vals) if vals else 0

    # =====================================================================
    # GRÁFICO 1: Barras agrupadas por critério
    # =====================================================================
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    x = np.arange(len(criterios))
    width = 0.11
    colors = ['#2d2d2d', '#666666', '#888888', '#aaaaaa', '#bbbbbb', '#cccccc', '#eeeeee']

    for i, (a, label) in enumerate(zip(abordagens, abordagens_labels)):
        vals = [means[a][c] for c in criterios]
        bars = ax.bar(x + i * width - 3 * width, vals, width,
                      label=label.replace('\n', ' '), color=colors[i],
                      edgecolor='black', linewidth=0.5)

    ax.set_xlabel('Critério de Avaliação', fontsize=12, fontfamily='Arial')
    ax.set_ylabel('Nota Média (0-10)', fontsize=12, fontfamily='Arial')
    ax.set_title('Comparação de Abordagens Arquiteturais por Critério',
                 fontsize=14, fontfamily='Arial', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(criterios_labels, fontsize=9, fontfamily='Arial')
    ax.set_ylim(0, 10.5)
    ax.legend(fontsize=9, ncol=7, loc='upper center', bbox_to_anchor=(0.5, -0.12))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    plt.tight_layout()
    plt.savefig(EXPERIMENT_DIR / 'grafico_criterios.png', dpi=200,
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("Gráfico 1 salvo: grafico_criterios.png")

    # =====================================================================
    # GRÁFICO 2: Média geral por abordagem
    # =====================================================================
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    medias_gerais = []
    for a in abordagens:
        all_vals = [means[a][c] for c in criterios]
        medias_gerais.append(sum(all_vals) / len(all_vals) if all_vals else 0)

    bars = ax.barh(range(len(abordagens)), medias_gerais, color=colors,
                   edgecolor='black', linewidth=0.8)

    ax.set_yticks(range(len(abordagens)))
    ax.set_yticklabels([l.replace('\n', ' ') for l in abordagens_labels],
                       fontsize=11, fontfamily='Arial')
    ax.set_xlabel('Nota Média Geral (0-10)', fontsize=12, fontfamily='Arial')
    ax.set_title('Média Geral por Abordagem Arquitetural',
                 fontsize=14, fontfamily='Arial', fontweight='bold')
    ax.set_xlim(0, 10.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    # Adicionar valores nas barras
    for bar, val in zip(bars, medias_gerais):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}', va='center', fontsize=11, fontfamily='Arial')

    plt.tight_layout()
    plt.savefig(EXPERIMENT_DIR / 'grafico_media_geral.png', dpi=200,
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("Gráfico 2 salvo: grafico_media_geral.png")

    # =====================================================================
    # GRÁFICO 3: Radar/Spider por abordagem
    # =====================================================================
    fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(polar=True))

    angles = np.linspace(0, 2 * np.pi, len(criterios), endpoint=False).tolist()
    angles += angles[:1]

    radar_abordagens = ["aoen", "clean_arch", "hexagonal", "sem_framework"]
    radar_labels = ["AOEN", "Clean Arch", "Hexagonal", "Sem Framework"]
    radar_colors = ['#2d2d2d', '#888888', '#aaaaaa', '#dddddd']
    radar_styles = ['-', '--', '-.', ':']

    for a, label, color, style in zip(radar_abordagens, radar_labels, radar_colors, radar_styles):
        vals = [means[a][c] for c in criterios]
        vals += vals[:1]
        ax.plot(angles, vals, style, linewidth=2, label=label, color=color)
        ax.fill(angles, vals, alpha=0.05, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criterios_labels, fontsize=8, fontfamily='Arial')
    ax.set_ylim(0, 10)
    ax.set_title('Perfil Comparativo: AOEN vs Selecionados',
                 fontsize=14, fontfamily='Arial', fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)

    plt.tight_layout()
    plt.savefig(EXPERIMENT_DIR / 'grafico_radar.png', dpi=200,
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("Gráfico 3 salvo: grafico_radar.png")

    # =====================================================================
    # Resumo numérico
    # =====================================================================
    print("\n" + "="*60)
    print("RESUMO: MÉDIA GERAL POR ABORDAGEM")
    print("="*60)
    for a, label, media in sorted(zip(abordagens, abordagens_labels, medias_gerais),
                                    key=lambda x: -x[2]):
        print(f"  {label.replace(chr(10), ' '):20s} {media:.2f}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "proto":
            run_batch(start=0, end=2, max_workers=3)
            consolidate()
            generate_charts()
        elif cmd == "run":
            run_batch(start=0, end=100, max_workers=5)
            consolidate()
            generate_charts()
        elif cmd == "charts":
            consolidate()
            generate_charts()
        elif cmd.startswith("batch"):
            # batch:0:10
            parts = cmd.split(":")
            s, e = int(parts[1]), int(parts[2])
            run_batch(start=s, end=e, max_workers=5)
        else:
            print(f"Comando desconhecido: {cmd}")
    else:
        print("Uso:")
        print("  python run_experiment.py proto    — Protótipo (2 ideias)")
        print("  python run_experiment.py run      — Completo (100 ideias)")
        print("  python run_experiment.py batch:0:10 — Lote parcial")
        print("  python run_experiment.py charts   — Só gerar gráficos")
