# -*- coding: utf-8 -*-
"""
Re-rodar AOEN com prompt corrigido (campos de custo detalhados)
+ re-avaliar com 10 especialistas.
100 execuções AOEN + 1000 avaliações especialistas.
"""
import json
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, ".")
from experimento_aoen import IDEIAS, PROMPT_AOEN
from run_specialists import SPECIALISTS, PROMPT_SPECIALIST

RESULTS_DIR = Path("experimento/results")
SPECIALISTS_DIR = RESULTS_DIR / "specialists"
SPECIALISTS_DIR.mkdir(parents=True, exist_ok=True)


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


def run_aoen(i):
    ideia = IDEIAS[i]
    f = RESULTS_DIR / f"idea_{i:03d}_aoen_v3.json"
    if f.exists():
        return (i, "SKIP")
    prompt = PROMPT_AOEN.format(ideia=ideia)
    response = run_claude(prompt)
    parsed = extract_json(response)
    with open(f, "w", encoding="utf-8") as fh:
        json.dump({"ideia_idx": i, "ideia": ideia, "abordagem": "aoen_v3",
                    "response": parsed}, fh, ensure_ascii=False, indent=2)
    return (i, "OK")


def eval_specialist(i, criterio):
    out_file = SPECIALISTS_DIR / f"spec_{i:03d}_aoen_v3_{criterio}.json"
    if out_file.exists():
        with open(out_file, "r", encoding="utf-8") as f:
            return json.load(f)

    idea_file = RESULTS_DIR / f"idea_{i:03d}_aoen_v3.json"
    if not idea_file.exists():
        return None

    with open(idea_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    response = data.get("response", {})
    if "raw_response" in response and str(response["raw_response"]).startswith("ERROR"):
        return None

    spec = SPECIALISTS[criterio]
    prompt = PROMPT_SPECIALIST.format(
        role=spec["role"],
        ideia=IDEIAS[i],
        resposta=json.dumps(response, ensure_ascii=False, indent=2)[:3000],
        prompt=spec["prompt"]
    )
    raw = run_claude(prompt)
    parsed = extract_json(raw)

    result = {
        "ideia_idx": i, "abordagem": "aoen_v3", "criterio": criterio,
        "especialista": spec["role"],
        "nota": parsed.get("nota"), "justificativa": parsed.get("justificativa", ""),
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def main():
    criterios = list(SPECIALISTS.keys())

    # FASE 1: AOEN v3
    print(f"{'='*60}")
    print("FASE 1: Re-rodar AOEN com prompt v3 (100 execuções)")
    print(f"{'='*60}\n")

    done = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(run_aoen, i): i for i in range(100)}
        for future in as_completed(futures):
            done += 1
            idx, status = future.result()
            if done % 20 == 0:
                print(f"  [{done}/100] progresso...", flush=True)

    print(f"  AOEN v3: {done} execuções")

    # FASE 2: Avaliar AOEN v3 com especialistas
    total = 100 * len(criterios)
    print(f"\n{'='*60}")
    print(f"FASE 2: Avaliar AOEN v3 com 10 especialistas ({total} avaliações)")
    print(f"{'='*60}\n")

    done = 0
    for i in range(100):
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(eval_specialist, i, cr): cr for cr in criterios}
            for future in as_completed(futures):
                done += 1
        if (i + 1) % 20 == 0:
            print(f"  [{done}/{total}] progresso...", flush=True)

    # CONSOLIDAR
    print(f"\n{'='*60}")
    print("RESULTADOS: AOEN v3 vs AOEN v1 vs outros")
    print(f"{'='*60}\n")

    # AOEN v3
    aoen_v3 = {c: [] for c in criterios}
    for f in sorted(SPECIALISTS_DIR.glob("spec_*_aoen_v3_*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        cr = d["criterio"]
        nota = d.get("nota")
        if isinstance(nota, (int, float)):
            aoen_v3[cr].append(nota)

    # AOEN v1 (especialistas anteriores)
    aoen_v1 = {c: [] for c in criterios}
    for f in sorted(SPECIALISTS_DIR.glob("spec_*_aoen_*.json")):
        if "_aoen_v3_" in f.name:
            continue
        with open(f, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        cr = d["criterio"]
        nota = d.get("nota")
        if isinstance(nota, (int, float)):
            aoen_v1[cr].append(nota)

    print(f"{'Critério':30s} {'AOEN v1':>8s} {'AOEN v3':>8s} {'Delta':>8s}")
    print("-" * 58)
    v1_total = []
    v3_total = []
    for c in criterios:
        m1 = sum(aoen_v1[c]) / len(aoen_v1[c]) if aoen_v1[c] else 0
        m3 = sum(aoen_v3[c]) / len(aoen_v3[c]) if aoen_v3[c] else 0
        v1_total.append(m1)
        v3_total.append(m3)
        delta = m3 - m1
        marker = " <<<" if abs(delta) > 1 else ""
        print(f"  {c:28s} {m1:8.1f} {m3:8.1f} {delta:+8.1f}{marker}")

    avg1 = sum(v1_total) / len(v1_total)
    avg3 = sum(v3_total) / len(v3_total)
    print(f"\n  {'MÉDIA':28s} {avg1:8.2f} {avg3:8.2f} {avg3-avg1:+8.2f}")

    # Mostrar justificativas de custo
    print(f"\n{'='*60}")
    print("JUSTIFICATIVAS DO ESPECIALISTA DE CUSTO (AOEN v3)")
    print(f"{'='*60}\n")
    for f in sorted(SPECIALISTS_DIR.glob("spec_*_aoen_v3_custo_por_cliente.json"))[:5]:
        with open(f, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        print(f"Ideia {d['ideia_idx']}: nota={d['nota']}")
        print(f"  {d['justificativa'][:200]}")
        print()

    for f in sorted(SPECIALISTS_DIR.glob("spec_*_aoen_v3_custo_infraestrutura.json"))[:5]:
        with open(f, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        print(f"Ideia {d['ideia_idx']} (infra): nota={d['nota']}")
        print(f"  {d['justificativa'][:200]}")
        print()


if __name__ == "__main__":
    main()
