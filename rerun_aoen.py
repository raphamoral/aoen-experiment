# -*- coding: utf-8 -*-
"""Re-rodar só o AOEN com prompt corrigido + re-avaliar com v2."""
import json
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, ".")
from experimento_aoen import IDEIAS, PROMPT_AOEN
from run_eval_v2 import PROMPT_AVALIADOR_V2

RESULTS_DIR = Path("experimento/results")


def run_claude(prompt):
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", "sonnet"],
            input=prompt,
            capture_output=True, text=True, encoding="utf-8"
        )
        return result.stdout.strip() if result.returncode == 0 else f"ERROR: {result.stderr}"
    except Exception as e:
        return f"ERROR: {str(e)}"


def extract_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return {"raw_response": text}


def run_one(i):
    ideia = IDEIAS[i]

    # 1. Gerar resposta AOEN com prompt corrigido
    idea_file = RESULTS_DIR / f"idea_{i:03d}_aoen_v2.json"
    if not idea_file.exists():
        prompt = PROMPT_AOEN.format(ideia=ideia)
        response = run_claude(prompt)
        parsed = extract_json(response)
        with open(idea_file, "w", encoding="utf-8") as f:
            json.dump({"ideia_idx": i, "ideia": ideia, "abordagem": "aoen_v2",
                        "response": parsed}, f, ensure_ascii=False, indent=2)
    else:
        with open(idea_file, "r", encoding="utf-8") as f:
            parsed = json.load(f)["response"]

    # 2. Avaliar com v2
    eval_file = RESULTS_DIR / f"eval_v2_{i:03d}_aoen_v2.json"
    if not eval_file.exists():
        eval_prompt = PROMPT_AVALIADOR_V2.format(
            ideia=ideia, abordagem="aoen",
            resposta=json.dumps(parsed, ensure_ascii=False, indent=2)[:3000]
        )
        raw = run_claude(eval_prompt)
        scores = extract_json(raw)
        with open(eval_file, "w", encoding="utf-8") as f:
            json.dump({"ideia_idx": i, "abordagem": "aoen_v2",
                        "scores": scores}, f, ensure_ascii=False, indent=2)
        return (i, "OK", scores)
    else:
        with open(eval_file, "r", encoding="utf-8") as f:
            return (i, "SKIP", json.load(f)["scores"])


def main():
    print(f"Re-rodando AOEN com prompt corrigido (100 ideias)...\n")
    done = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(run_one, i): i for i in range(100)}
        for future in as_completed(futures):
            i = futures[future]
            done += 1
            try:
                idx, status, scores = future.result()
                infra = scores.get("custo_infraestrutura", "?")
                cliente = scores.get("custo_por_cliente", "?")
                print(f"  [{done:3d}/100] ideia {idx}: {status} infra={infra} cliente={cliente}", flush=True)
            except Exception as e:
                print(f"  [{done:3d}/100] ideia {i}: ERROR {e}", flush=True)

    # Consolidar
    criterios = ["core_diferenciador", "visao_mercado", "multi_interface",
                 "configurabilidade", "isolamento_processamento",
                 "custo_infraestrutura", "custo_por_cliente",
                 "monetizacao", "evolucao", "coerencia"]

    all_scores = {c: [] for c in criterios}
    for f in sorted(RESULTS_DIR.glob("eval_v2_*_aoen_v2.json")):
        with open(f, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        sc = d.get("scores", {})
        if "raw_response" in sc:
            continue
        for c in criterios:
            v = sc.get(c)
            if isinstance(v, (int, float)):
                all_scores[c].append(v)

    print(f"\n{'='*50}")
    print("AOEN v2 (prompt corrigido) — 100 ideias")
    print(f"{'='*50}")
    for c in criterios:
        vals = all_scores[c]
        avg = sum(vals) / len(vals) if vals else 0
        print(f"  {c:30s} {avg:5.1f} (n={len(vals)})")

    total = [sum(all_scores[c]) / len(all_scores[c]) for c in criterios if all_scores[c]]
    print(f"\n  {'MÉDIA GERAL':30s} {sum(total)/len(total):5.2f}")


if __name__ == "__main__":
    main()
