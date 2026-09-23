# -*- coding: utf-8 -*-
"""
Experimento V2 completo:
1. Re-rodar AOEN com prompt corrigido (100 execuções)
2. Re-avaliar TODOS os 7 com avaliador v2 (700 avaliações)
"""
import json
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, ".")
from experimento_aoen import IDEIAS, PROMPT_AOEN
from run_eval_v2 import PROMPT_AVALIADOR_V2

RESULTS_DIR = Path("experimento/results")
ABORDAGENS = ["aoen", "clean_arch", "hexagonal", "12factor",
              "evolutionary", "arch_flow", "sem_framework"]


def run_claude(prompt):
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", "sonnet"],
            input=prompt, capture_output=True, text=True, encoding="utf-8"
        )
        return result.stdout.strip() if result.returncode == 0 else f"ERROR: {result.stderr}"
    except Exception as e:
        return f"ERROR: {str(e)}"


def extract_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    s = text.find("{")
    e = text.rfind("}") + 1
    if s >= 0 and e > s:
        try:
            return json.loads(text[s:e])
        except json.JSONDecodeError:
            pass
    return {"raw_response": text}


# =====================================================================
# FASE 1: Re-rodar AOEN com prompt corrigido
# =====================================================================
def run_aoen(i):
    ideia = IDEIAS[i]
    f = RESULTS_DIR / f"idea_{i:03d}_aoen_v2.json"
    if f.exists():
        return (i, "SKIP")
    prompt = PROMPT_AOEN.format(ideia=ideia)
    response = run_claude(prompt)
    parsed = extract_json(response)
    with open(f, "w", encoding="utf-8") as fh:
        json.dump({"ideia_idx": i, "ideia": ideia, "abordagem": "aoen_v2",
                    "response": parsed}, fh, ensure_ascii=False, indent=2)
    return (i, "OK")


# =====================================================================
# FASE 2: Re-avaliar todos com critério v2
# =====================================================================
def eval_one(i, ab):
    # Para AOEN, usar resposta v2. Para outros, usar resposta original.
    if ab == "aoen":
        idea_file = RESULTS_DIR / f"idea_{i:03d}_aoen_v2.json"
        if not idea_file.exists():
            idea_file = RESULTS_DIR / f"idea_{i:03d}_aoen.json"
    else:
        idea_file = RESULTS_DIR / f"idea_{i:03d}_{ab}.json"

    eval_file = RESULTS_DIR / f"eval_v2_full_{i:03d}_{ab}.json"
    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as fh:
            return json.load(fh)

    if not idea_file.exists():
        return None

    with open(idea_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    response = data.get("response", {})
    if "raw_response" in response and str(response["raw_response"]).startswith("ERROR"):
        return None

    ideia = IDEIAS[i]
    prompt = PROMPT_AVALIADOR_V2.format(
        ideia=ideia, abordagem=ab,
        resposta=json.dumps(response, ensure_ascii=False, indent=2)[:3000]
    )
    raw = run_claude(prompt)
    scores = extract_json(raw)
    result = {"ideia_idx": i, "abordagem": ab, "scores": scores}
    with open(eval_file, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    return result


def main():
    # FASE 1: AOEN
    print(f"{'='*60}")
    print("FASE 1: Re-rodar AOEN com prompt corrigido (100 execuções)")
    print(f"{'='*60}\n")

    done = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(run_aoen, i): i for i in range(100)}
        for future in as_completed(futures):
            done += 1
            i = futures[future]
            try:
                idx, status = future.result()
                if done % 10 == 0 or status == "OK":
                    print(f"  [{done:3d}/100] ideia {idx}: {status}", flush=True)
            except Exception as e:
                print(f"  [{done:3d}/100] ideia {i}: ERROR {e}", flush=True)

    print(f"\nAOEN: {done} execuções completas")

    # FASE 2: Avaliar todos
    print(f"\n{'='*60}")
    print("FASE 2: Re-avaliar TODOS com avaliador v2 (700 avaliações)")
    print(f"{'='*60}\n")

    done = 0
    total = 100 * len(ABORDAGENS)

    for i in range(100):
        ideia = IDEIAS[i]
        if i % 10 == 0:
            print(f"\n[Ideia {i+1}/100] {ideia[:50]}...", flush=True)

        with ThreadPoolExecutor(max_workers=7) as executor:
            futures = {executor.submit(eval_one, i, ab): ab for ab in ABORDAGENS}
            for future in as_completed(futures):
                ab = futures[future]
                done += 1
                try:
                    result = future.result()
                    if result and "raw_response" not in result.get("scores", {}):
                        status = "OK"
                    else:
                        status = "SKIP" if result is None else "RAW"
                except Exception as e:
                    status = f"ERR"
                if done % 50 == 0:
                    print(f"  [{done}/{total}] progresso...", flush=True)

    # CONSOLIDAR
    print(f"\n{'='*60}")
    print("CONSOLIDANDO RESULTADOS")
    print(f"{'='*60}\n")

    criterios = ["core_diferenciador", "visao_mercado", "multi_interface",
                 "configurabilidade", "isolamento_processamento",
                 "custo_infraestrutura", "custo_por_cliente",
                 "monetizacao", "evolucao", "coerencia"]

    all_evals = []
    for f in sorted(RESULTS_DIR.glob("eval_v2_full_*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            all_evals.append(json.load(fh))

    with open("experimento/consolidated_v2_full.json", "w", encoding="utf-8") as f:
        json.dump(all_evals, f, ensure_ascii=False, indent=2)

    scores = {a: {c: [] for c in criterios} for a in ABORDAGENS}
    for ev in all_evals:
        ab = ev["abordagem"]
        sc = ev.get("scores", {})
        if "raw_response" in sc:
            continue
        for c in criterios:
            v = sc.get(c)
            if isinstance(v, (int, float)):
                scores[ab][c].append(v)

    # Tabela completa
    print(f"{'Abordagem':20s}", end="")
    for c in criterios:
        print(f" {c[:8]:>8s}", end="")
    print(f" {'MÉDIA':>7s}")
    print("-" * 115)

    for ab in sorted(ABORDAGENS, key=lambda a: -sum(
        sum(scores[a][c])/max(len(scores[a][c]),1) for c in criterios)/len(criterios)):
        print(f"{ab:20s}", end="")
        vals = []
        for c in criterios:
            v = scores[ab][c]
            m = sum(v)/len(v) if v else 0
            vals.append(m)
            print(f" {m:8.1f}", end="")
        media = sum(vals)/len(vals)
        print(f" {media:7.2f}")

    print(f"\nTotal avaliações: {len(all_evals)}")
    print(f"Consolidado em: experimento/consolidated_v2_full.json")


if __name__ == "__main__":
    main()
