# -*- coding: utf-8 -*-
"""Re-rodar avaliações com critério de custo separado (infra vs cliente)."""
import json
import os
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

RESULTS_DIR = Path("experimento/results")

with open("experimento/ideias.json", "r", encoding="utf-8") as f:
    IDEIAS = json.load(f)

ABORDAGENS = ["aoen", "clean_arch", "hexagonal", "12factor",
              "evolutionary", "arch_flow", "sem_framework"]

PROMPT_AVALIADOR_V2 = """Você é um avaliador neutro de arquiteturas de software. Analise a seguinte proposta arquitetural para o produto "{ideia}" e avalie cada critério com uma nota de 0 a 10.

Proposta (abordagem: {abordagem}):
{resposta}

Avalie com notas de 0 a 10 para cada critério:
{{
  "core_diferenciador": <0-10: Identificou um núcleo tecnológico diferenciador claro?>,
  "visao_mercado": <0-10: Considerou o mercado-alvo e proposta de valor?>,
  "multi_interface": <0-10: Previu múltiplas interfaces para diferentes contextos de uso?>,
  "configurabilidade": <0-10: Previu comportamento configurável por cliente sem código?>,
  "isolamento_processamento": <0-10: Isolou processamento pesado/caro do resto?>,
  "custo_infraestrutura": <0-10: Considerou custos de infraestrutura (servidores, banco, hospedagem, CDN, armazenamento)?>,
  "custo_por_cliente": <0-10: Previu mensuração de custo por operação ou por cliente/tenant para viabilizar precificação?>,
  "monetizacao": <0-10: Previu modelo de monetização viável?>,
  "evolucao": <0-10: A arquitetura permite evoluir sem reescrever?>,
  "coerencia": <0-10: As decisões se conectam e reforçam mutuamente?>
}}

Responda APENAS o JSON com as notas numéricas, sem texto adicional."""


def run_claude(prompt):
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


def evaluate_one(ideia_idx, abordagem):
    eval_file = RESULTS_DIR / f"eval_v2_{ideia_idx:03d}_{abordagem}.json"
    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # Ler resposta original
    idea_file = RESULTS_DIR / f"idea_{ideia_idx:03d}_{abordagem}.json"
    if not idea_file.exists():
        return None

    with open(idea_file, "r", encoding="utf-8") as f:
        idea_data = json.load(f)

    response = idea_data.get("response", {})
    if "raw_response" in response and response["raw_response"].startswith("ERROR"):
        return None

    ideia = IDEIAS[ideia_idx]
    prompt = PROMPT_AVALIADOR_V2.format(
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


def main():
    total = len(IDEIAS) * len(ABORDAGENS)
    done = 0

    print(f"{'='*60}")
    print(f"AVALIAÇÃO V2 — 10 critérios (custo separado)")
    print(f"{total} avaliações")
    print(f"{'='*60}\n")

    for i in range(len(IDEIAS)):
        ideia = IDEIAS[i]
        print(f"[Ideia {i+1}/100] {ideia[:50]}...", flush=True)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            for ab in ABORDAGENS:
                f = executor.submit(evaluate_one, i, ab)
                futures[f] = ab

            for future in as_completed(futures):
                ab = futures[future]
                done += 1
                try:
                    result = future.result()
                    if result and "raw_response" not in result.get("scores", {}):
                        status = "OK"
                    else:
                        status = "SKIP" if result is None else "RAW"
                    print(f"  [{done}/{total}] {ab}: {status}", flush=True)
                except Exception as e:
                    print(f"  [{done}/{total}] {ab}: ERROR - {e}", flush=True)

    # Consolidar
    all_evals = []
    for f in sorted(RESULTS_DIR.glob("eval_v2_*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            all_evals.append(json.load(fh))

    with open("experimento/consolidated_v2.json", "w", encoding="utf-8") as f:
        json.dump(all_evals, f, ensure_ascii=False, indent=2)

    print(f"\nConsolidado: {len(all_evals)} avaliações em consolidated_v2.json")

    # Resumo
    criterios = ["core_diferenciador", "visao_mercado", "multi_interface",
                 "configurabilidade", "isolamento_processamento",
                 "custo_infraestrutura", "custo_por_cliente",
                 "monetizacao", "evolucao", "coerencia"]

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

    print(f"\n{'='*60}")
    print("RESULTADOS V2")
    print(f"{'='*60}")
    print(f"{'Abordagem':20s} {'Infra':>6s} {'Cliente':>8s} {'Média':>7s}")
    print("-" * 45)

    for ab in sorted(ABORDAGENS, key=lambda a: -(sum(scores[a]['custo_infraestrutura'])/max(len(scores[a]['custo_infraestrutura']),1) + sum(scores[a]['custo_por_cliente'])/max(len(scores[a]['custo_por_cliente']),1))/2):
        infra = scores[ab]['custo_infraestrutura']
        cliente = scores[ab]['custo_por_cliente']
        mi = sum(infra)/len(infra) if infra else 0
        mc = sum(cliente)/len(cliente) if cliente else 0
        media_geral = sum(sum(scores[ab][c])/len(scores[ab][c]) for c in criterios if scores[ab][c]) / len(criterios)
        print(f"{ab:20s} {mi:6.1f} {mc:8.1f} {media_geral:7.2f}")


if __name__ == "__main__":
    main()
