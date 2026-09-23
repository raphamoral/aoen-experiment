# -*- coding: utf-8 -*-
"""
Avaliação V3 — 10 especialistas independentes.
Cada especialista avalia SÓ seu critério com profundidade.
700 respostas x 10 especialistas = 7.000 avaliações.
"""
import json
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

RESULTS_DIR = Path("experimento/results")
SPECIALISTS_DIR = RESULTS_DIR / "specialists"
SPECIALISTS_DIR.mkdir(parents=True, exist_ok=True)

with open("experimento/ideias.json", "r", encoding="utf-8") as f:
    IDEIAS = json.load(f)

ABORDAGENS = ["aoen", "clean_arch", "hexagonal", "12factor",
              "evolutionary", "arch_flow", "sem_framework"]

# =====================================================================
# 10 ESPECIALISTAS — cada um com contexto profundo do seu critério
# =====================================================================

SPECIALISTS = {
    "core_diferenciador": {
        "role": "Especialista em Produto e Inovação",
        "prompt": """Você é um especialista em desenvolvimento de produto e inovação tecnológica com 15 anos de experiência em startups SaaS. Sua especialidade é identificar o que torna um produto único e insubstituível no mercado.

Avalie APENAS este critério — NÚCLEO DIFERENCIADOR:
- O produto tem um componente tecnológico que o define? Sem esse componente, o produto perderia razão de existir?
- O núcleo é claramente identificado e separado do restante?
- O núcleo é extensível (não depende de um único fornecedor)?
- O núcleo resolve um problema real de forma que alternativas existentes não resolvem?

Nota 0: Não identificou nenhum diferenciador. É um CRUD genérico.
Nota 5: Identificou um diferenciador mas não o isolou ou não explicou por que é único.
Nota 10: Diferenciador claro, isolado, extensível e com proposta de valor insubstituível."""
    },

    "visao_mercado": {
        "role": "Especialista em Estratégia de Mercado e Go-to-Market",
        "prompt": """Você é um especialista em estratégia de mercado e go-to-market com experiência em lançamento de produtos B2B e B2C SaaS. Sua especialidade é avaliar se um produto tem mercado-alvo claro e estratégia viável.

Avalie APENAS este critério — VISÃO DE MERCADO:
- O mercado-alvo está claramente definido (quem são os usuários, qual o tamanho do mercado)?
- A dor do cliente está articulada (não apenas o que o produto faz, mas POR QUE o cliente precisa)?
- Há diferenciação clara em relação a alternativas existentes?
- A proposta de valor é convincente o suficiente para justificar adoção?

Nota 0: Nenhuma menção a mercado ou público-alvo.
Nota 5: Mencionou público-alvo mas sem profundidade sobre dor, tamanho ou diferenciação.
Nota 10: Mercado-alvo preciso, dor articulada, diferenciação clara e proposta de valor convincente."""
    },

    "multi_interface": {
        "role": "Especialista em UX e Plataformas Multi-canal",
        "prompt": """Você é um especialista em experiência do usuário e design de plataformas multi-canal com experiência em produtos que atendem usuários em diferentes contextos (web, mobile, CLI, API).

Avalie APENAS este critério — MÚLTIPLAS INTERFACES:
- O projeto prevê mais de uma interface para diferentes contextos de uso?
- Cada interface é justificada por um perfil de usuário ou caso de uso real?
- A lógica de negócio está desacoplada das interfaces (pode adicionar nova interface sem reescrever)?
- As interfaces foram escolhidas por alcance de mercado, não por conveniência técnica?

Nota 0: Uma única interface, sem consideração de contextos diferentes.
Nota 5: Mencionou múltiplas interfaces mas sem desacoplamento ou justificativa de mercado.
Nota 10: Múltiplas interfaces justificadas por mercado, com lógica desacoplada e possibilidade de expansão."""
    },

    "configurabilidade": {
        "role": "Especialista em Arquitetura SaaS Multi-tenant",
        "prompt": """Você é um especialista em arquitetura SaaS multi-tenant com experiência em escalar produtos para centenas de clientes sem código customizado por cliente.

Avalie APENAS este critério — CONFIGURABILIDADE POR CLIENTE:
- O sistema permite comportamento diferente por cliente/tenant sem alterar código?
- O fluxo principal é genérico (fixo no código) com parâmetros configuráveis?
- Novo cliente pode ser onboardado apenas com configuração (sem deploy ou desenvolvimento)?
- Há clara separação entre o que é código (fixo) e o que é configuração (variável por cliente)?

Nota 0: Tudo hardcoded. Novo cliente exigiria fork ou código novo.
Nota 5: Alguma configuração existe mas parcial — ainda exige código para novos clientes.
Nota 10: Comportamento totalmente dirigido por configuração. Novo cliente = nova row no banco, zero código."""
    },

    "isolamento_processamento": {
        "role": "Especialista em Engenharia de Resiliência e Sistemas Distribuídos",
        "prompt": """Você é um especialista em engenharia de resiliência e sistemas distribuídos com experiência no padrão Bulkhead, circuit breakers e isolamento de processos críticos.

Avalie APENAS este critério — ISOLAMENTO DE PROCESSAMENTO:
- Processos computacionalmente pesados ou caros estão isolados do restante da aplicação?
- Se o processo pesado falhar, o restante do sistema continua funcionando?
- O processamento pesado roda de forma assíncrona (filas, workers, subprocessos)?
- O isolamento é físico (processo separado) ou apenas lógico (mesma aplicação, threads)?
- O isolamento permite escalar o processamento pesado independentemente?

Nota 0: Tudo roda junto. Falha no processamento pesado derruba tudo.
Nota 5: Mencionou processamento assíncrono mas sem isolamento físico real ou sem resiliência a falhas.
Nota 10: Processamento pesado em processo/worker separado, assíncrono, com fallback em caso de falha e escalável independentemente."""
    },

    "custo_infraestrutura": {
        "role": "Especialista em FinOps e Infraestrutura Cloud",
        "prompt": """Você é um especialista em FinOps (Financial Operations) e infraestrutura cloud com experiência em otimização de custos AWS/GCP/Azure para startups e scale-ups.

Avalie APENAS este critério — CUSTO DE INFRAESTRUTURA:
- O projeto considerou os custos de infraestrutura (servidores, banco de dados, CDN, armazenamento, banda)?
- Há estimativas concretas de custo (valores em dólares/reais, não apenas "vai usar S3")?
- A arquitetura foi desenhada para otimizar custos (scale-to-zero, instâncias spot, tier de armazenamento)?
- Há consideração de como os custos crescem com a base de usuários?

Nota 0: Nenhuma menção a custos de infraestrutura.
Nota 5: Listou componentes de infra mas sem valores estimados ou sem estratégia de otimização.
Nota 10: Estimativas concretas de custo por componente, estratégia de otimização e projeção de crescimento."""
    },

    "custo_por_cliente": {
        "role": "Especialista em Precificação e Unit Economics de SaaS",
        "prompt": """Você é um especialista em precificação de produtos SaaS e unit economics com experiência em modelar custo por cliente (CAC, LTV, margem por tenant).

Avalie APENAS este critério — CUSTO POR CLIENTE/TENANT:
- O projeto prevê mensuração de custo POR CLIENTE, não apenas custo total de infra?
- O custo por operação/transação é calculável (ex: "cada análise custa R$0,50 de IA + R$0,01 de storage")?
- A arquitetura permite rastrear quanto cada tenant consome de recursos?
- O custo por cliente está conectado ao modelo de precificação (sabe-se a margem por cliente)?
- Há diferença entre calcular custo total de infra (FinOps) e calcular custo por cliente (Unit Economics)?

ATENÇÃO: Um projeto que diz "servidor custa $50/mês" está listando infra, NÃO calculando custo por cliente. Um projeto que diz "cada operação custa R$0,003 por cliente" ESTÁ calculando custo por cliente. São coisas diferentes.

Nota 0: Nenhuma mensuração por cliente. Custos tratados apenas como total.
Nota 5: Mencionou custo variável mas sem cálculo real por cliente/operação.
Nota 10: Cálculo detalhado de custo por cliente/operação, com rastreamento por tenant e conexão com precificação."""
    },

    "monetizacao": {
        "role": "Especialista em Modelos de Negócio e Monetização SaaS",
        "prompt": """Você é um especialista em modelos de negócio e monetização de produtos SaaS com experiência em freemium, subscription, usage-based pricing e marketplace.

Avalie APENAS este critério — MONETIZAÇÃO:
- O projeto prevê um modelo de monetização claro e viável?
- O modelo de receita está conectado ao valor entregue ao cliente (cobra por algo que o cliente valoriza)?
- Há tiers ou planos que permitem capturar valor de diferentes segmentos?
- O modelo é sustentável (a receita por cliente supera o custo por cliente)?
- Há consideração de métricas de negócio (MRR, churn, LTV, CAC)?

Nota 0: Nenhuma menção a como o produto gera receita.
Nota 5: Mencionou um modelo genérico ("assinatura mensal") sem detalhes de tiers, valores ou sustentabilidade.
Nota 10: Modelo detalhado com tiers, valores, conexão custo-receita e métricas de sustentabilidade."""
    },

    "evolucao": {
        "role": "Especialista em Arquitetura Evolutiva e Manutenibilidade",
        "prompt": """Você é um especialista em arquitetura evolutiva e manutenibilidade de software com experiência em sistemas que crescem e mudam ao longo de anos sem necessidade de reescrita.

Avalie APENAS este critério — EVOLUÇÃO:
- A arquitetura permite adicionar funcionalidades sem reescrever o existente?
- Componentes podem ser substituídos independentemente (ex: trocar banco, trocar framework de IA)?
- As dependências apontam para dentro (lógica de negócio não depende de frameworks externos)?
- O sistema pode crescer de 10 para 10.000 usuários sem mudança arquitetural fundamental?
- Decisões foram tomadas para serem reversíveis quando possível?

Nota 0: Monolito acoplado que exige reescrita para qualquer mudança significativa.
Nota 5: Alguma separação existe mas componentes-chave estão acoplados a tecnologias específicas.
Nota 10: Arquitetura modular onde cada componente pode evoluir independentemente, com decisões reversíveis."""
    },

    "coerencia": {
        "role": "Especialista em Arquitetura de Sistemas e Design Sistêmico",
        "prompt": """Você é um especialista em arquitetura de sistemas com visão holística, capaz de avaliar se as decisões de um projeto se reforçam mutuamente ou se contradizem.

Avalie APENAS este critério — COERÊNCIA:
- As decisões arquiteturais se conectam e reforçam mutuamente?
- Há contradições (ex: diz que precisa escalar mas hardcoda configurações)?
- O todo é maior que a soma das partes (as decisões criam um sistema coeso)?
- A escolha de tecnologias é consistente com os objetivos declarados?
- O projeto conta uma história coerente do problema à solução?

Nota 0: Decisões desconectadas, contraditórias ou sem relação entre si.
Nota 5: Algumas decisões se conectam mas há contradições ou lacunas evidentes.
Nota 10: Todas as decisões se reforçam mutuamente, formando um sistema coeso onde cada parte justifica as outras."""
    },
}

PROMPT_SPECIALIST = """Você é {role}.

Produto avaliado: "{ideia}"

Proposta arquitetural:
{resposta}

{prompt}

Responda APENAS com um JSON neste formato:
{{
  "nota": <0-10>,
  "justificativa": "<uma frase explicando a nota>"
}}"""


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


def eval_specialist(ideia_idx, abordagem, criterio):
    """Avalia uma resposta com um especialista."""
    out_file = SPECIALISTS_DIR / f"spec_{ideia_idx:03d}_{abordagem}_{criterio}.json"
    if out_file.exists():
        with open(out_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # Ler resposta (AOEN usa v2, outros usam original)
    if abordagem == "aoen":
        idea_file = RESULTS_DIR / f"idea_{ideia_idx:03d}_aoen_v2.json"
        if not idea_file.exists():
            idea_file = RESULTS_DIR / f"idea_{ideia_idx:03d}_aoen.json"
    else:
        idea_file = RESULTS_DIR / f"idea_{ideia_idx:03d}_{abordagem}.json"

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
        ideia=IDEIAS[ideia_idx],
        resposta=json.dumps(response, ensure_ascii=False, indent=2)[:3000],
        prompt=spec["prompt"]
    )

    raw = run_claude(prompt)
    parsed = extract_json(raw)

    result = {
        "ideia_idx": ideia_idx,
        "abordagem": abordagem,
        "criterio": criterio,
        "especialista": spec["role"],
        "nota": parsed.get("nota"),
        "justificativa": parsed.get("justificativa", ""),
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def main():
    criterios = list(SPECIALISTS.keys())
    total = len(IDEIAS) * len(ABORDAGENS) * len(criterios)
    done = 0

    print(f"{'='*70}")
    print(f"AVALIAÇÃO V3 — 10 ESPECIALISTAS INDEPENDENTES")
    print(f"{len(IDEIAS)} ideias x {len(ABORDAGENS)} abordagens x {len(criterios)} critérios = {total} avaliações")
    print(f"{'='*70}\n")

    for i in range(len(IDEIAS)):
        if i % 10 == 0:
            print(f"\n[Ideia {i+1}/100] {IDEIAS[i][:50]}...", flush=True)

        # Rodar todos os especialistas pra todas as abordagens dessa ideia em paralelo
        tasks = []
        for ab in ABORDAGENS:
            for cr in criterios:
                tasks.append((i, ab, cr))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(eval_specialist, i, ab, cr): (ab, cr)
                       for i2, ab, cr in tasks}
            for future in as_completed(futures):
                done += 1
                if done % 100 == 0:
                    print(f"  [{done}/{total}] progresso...", flush=True)

    # CONSOLIDAR
    print(f"\n{'='*70}")
    print("CONSOLIDANDO RESULTADOS")
    print(f"{'='*70}\n")

    all_results = []
    for f in sorted(SPECIALISTS_DIR.glob("spec_*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            all_results.append(json.load(fh))

    with open("experimento/consolidated_v3_specialists.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # Calcular médias
    scores = {a: {c: [] for c in criterios} for a in ABORDAGENS}
    for r in all_results:
        ab = r["abordagem"]
        cr = r["criterio"]
        nota = r.get("nota")
        if isinstance(nota, (int, float)):
            scores[ab][cr].append(nota)

    # Tabela
    print(f"{'Abordagem':20s}", end="")
    for c in criterios:
        print(f" {c[:8]:>8s}", end="")
    print(f" {'MÉDIA':>7s}")
    print("-" * 120)

    for ab in sorted(ABORDAGENS, key=lambda a: -sum(
            sum(scores[a][c]) / max(len(scores[a][c]), 1) for c in criterios) / len(criterios)):
        print(f"{ab:20s}", end="")
        vals = []
        for c in criterios:
            v = scores[ab][c]
            m = sum(v) / len(v) if v else 0
            vals.append(m)
            print(f" {m:8.1f}", end="")
        media = sum(vals) / len(vals)
        print(f" {media:7.2f}")

    print(f"\nTotal avaliações: {len(all_results)}")
    print(f"Consolidado em: experimento/consolidated_v3_specialists.json")

    # Comparação V1 vs V3
    print(f"\n{'='*70}")
    print("COMPARAÇÃO V1 (generalista) vs V3 (especialistas)")
    print(f"{'='*70}\n")
    v1_medias = {"aoen": 7.31, "arch_flow": 7.08, "hexagonal": 6.67,
                 "sem_framework": 6.34, "evolutionary": 5.99,
                 "12factor": 5.44, "clean_arch": 4.42}

    print(f"{'Abordagem':20s} {'V1 (gen.)':>10s} {'V3 (espec.)':>12s} {'Diferença':>10s}")
    print("-" * 55)
    for ab in sorted(ABORDAGENS, key=lambda a: -v1_medias.get(a, 0)):
        v1 = v1_medias.get(ab, 0)
        v3_vals = []
        for c in criterios:
            v = scores[ab][c]
            if v:
                v3_vals.append(sum(v) / len(v))
        v3 = sum(v3_vals) / len(v3_vals) if v3_vals else 0
        diff = v3 - v1
        print(f"{ab:20s} {v1:10.2f} {v3:12.2f} {diff:+10.2f}")


if __name__ == "__main__":
    main()
