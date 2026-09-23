# Experimento AOEN — pacote de replicação

Comparação controlada de sete abordagens arquiteturais aplicadas às mesmas 100
ideias de produtos SaaS, por **simulação in silico** com modelos de linguagem.

Este repositório contém tudo o que é necessário para reexecutar o experimento e
reproduzir os números publicados: as ideias, os prompts, a rubrica de avaliação,
os scripts, os resultados brutos e os projetos gerados.

Acompanha o TCC *"AOEN: arquitetura orgânica orientada a estratégia de negócio
aplicada a projetos SaaS"* (Raphael Moral Piazera, MBA em Engenharia de
Software, USP/Esalq).

---

## Resultados da rodada válida (v4)

100 ideias × 7 abordagens = 700 gerações e 700 avaliações, 9 critérios por
avaliação = **6.300 pontos de dados, cobertura 100%**.

| # | Abordagem | Média geral |
|---|---|---|
| 1 | **AOEN** | **8,91** |
| 2 | Architecture for Flow | 8,19 |
| 3 | Evolutionary Architecture | 8,05 |
| 4 | Twelve-Factor App | 7,84 |
| 5 | Sem framework (controle) | 7,69 |
| 6 | Hexagonal Architecture | 7,61 |
| 7 | Clean Architecture | 7,20 |

Na comparação pareada sobre as mesmas 100 ideias, o AOEN supera cada uma das
demais abordagens em pelo menos 97 dos 100 casos.

Modelo: `claude-sonnet-5`, fixado por id (não por alias), na geração e na
avaliação. Cada artefato registra o modelo e o hash do prompt que o produziu.

**Arquivo de referência:** `experimento/consolidated_v4.json`
**Artefatos brutos:** `experimento/results_v4/` (700 `idea_*.json` + 700 `eval_*.json`)

---

## Limitações conhecidas

Declaradas aqui porque são verificáveis neste repositório e a omissão seria pior
que o defeito.

**1. Os prompts não são simétricos.** O prompt do AOEN tem 3.833 caracteres
contra uma média de 1.176 dos seis concorrentes — razão de 3,3 para 1 — e
menciona explicitamente **oito dos nove critérios** da rubrica, enquanto os
concorrentes mencionam de três a cinco. Parte da vantagem observada pode decorrer
de o prompt instruir o modelo a tratar precisamente aquilo que o avaliador
pontua, e não da superioridade do framework. Separar as duas explicações exigiria
prompts normalizados em extensão e especificidade, ou uma rubrica construída
independentemente do framework avaliado. Nenhum desses controles foi aplicado.

**2. A avaliação não é cega.** O `PROMPT_AVALIADOR` informa ao avaliador o nome
da abordagem que gerou a proposta (`Proposta (abordagem: {abordagem})`).
Denominações como "sem framework" podem induzir expectativa antes da leitura.
Cegar os rótulos é a primeira melhoria para uma replicação.

**3. Gerador e avaliador são o mesmo modelo**, ainda que em execuções separadas.
Não é possível descartar concordância sistemática entre os dois papéis. Usar um
avaliador de outra família é a segunda melhoria.

**4. Modelos de linguagem são estocásticos.** Reexecuções produzem variação
numérica. Para comparabilidade, use o mesmo id de modelo, os prompts versionados
aqui e o mesmo conjunto de ideias.

---

## Rodadas anteriores (preservadas, não use para citar)

Os arquivos abaixo são de rodadas anteriores e estão mantidos por transparência.
**Nenhum deles sustenta os números publicados.**

| Arquivo | O que é | Por que não usar |
|---|---|---|
| `experimento/consolidated.json` | rodada de abril/2026 | 700 registros, mas só **147 avaliações válidas** (ideias 0–20). As outras 553 são `{"scores": {"raw_response": "ERROR: "}}`, resultado de rate limit do CLI por volta da ideia 21. O script da época gravava o erro como artefato e o pulava na retomada, então a falha passou despercebida. |
| `experimento/consolidated_v2.json` | rodada parcial | 22 ideias |
| `experimento/consolidated_v2_full.json` | rodada parcial | AOEN com 100 ideias, concorrentes com 22 — comparação desbalanceada |
| `experimento/consolidated_v3_specialists.json` | painel de 10 especialistas | desenho diferente (nota por critério e por persona), cobertura desigual entre braços |
| `experimento/results/` | artefatos da rodada de abril | contém os registros `ERROR:` |

O `runner.py` atual recusa-se a consolidar um conjunto incompleto e nomeia cada
buraco — foi escrito exatamente para impedir a repetição desse caso.

---

## Pré-requisitos

- Python 3.11+
- Claude CLI autenticado (`npm i -g @anthropic-ai/claude-code`, depois `claude login`)
- `matplotlib` e `numpy` para as figuras

Custo aproximado de uma rodada completa: ~4 M tokens de conteúdo (1.400 chamadas),
4 a 6 horas conforme o paralelismo e os limites da conta.

---

## Reproduzir

```bash
# estado atual
python runner.py --status --results experimento/results_v4

# estimativa antes de gastar
python runner.py --dry-run

# rodada completa (retomável)
python runner.py --workers 8 --results experimento/results_v4

# consolidar (recusa se houver buraco)
python runner.py --consolidate --results experimento/results_v4 --out consolidated_v4.json

# figuras
python gerar_figuras_v4.py          # média geral, radar, critérios
python gerar_figuras_restantes.py   # fases, eficiência, decisões, negócio×técnica, posicionamento
```

O `runner.py` é retomável: valida cada artefato antes de gravar, nunca escreve
um resultado inválido, recua e retenta em caso de limite de uso e, se o limite
persistir, para gravando o checkpoint. Rodar o mesmo comando continua de onde
parou. Pare com `Ctrl+C` ou criando um arquivo `STOP` na pasta.

Trilha de auditoria: `experimento/results_v4/_attempts.jsonl` (uma linha por
tentativa) e `_state.json` (checkpoint).

---

## Estrutura

```
experimento_aoen.py          100 ideias, 7 prompts de abordagem, PROMPT_AVALIADOR
runner.py                    runner retomável (recomendado)
run_experiment.py            runner original (histórico; ver rodadas anteriores)
legado/                      scripts de gráfico antigos, com valores cravados — não usar
gerar_figuras_v4.py          figuras a partir de consolidated_v4.json
gerar_figuras_restantes.py   demais figuras
experimento/
  ideias.json                as 100 ideias
  config.json                abordagens, critérios, contagens
  consolidated_v4.json       RESULTADO DE REFERÊNCIA
  results_v4/                artefatos brutos + log de tentativas
pocs/                        21 projetos gerados (3 ideias × 7 abordagens)
gerar_pocs.py                gerador dos projetos acima
figuras-revisao/             figuras numeradas conforme o TCC
```

As métricas de código dos 21 projetos (Tabelas 7 a 9 do TCC) foram extraídas de
`pocs/`, que está incluído na íntegra.

---

## O que não está aqui

O estudo de caso qualitativo do TCC (Fase 1) analisa dois projetos de produto do
autor. **O código-fonte desses projetos não integra este repositório**, por ser
software comercial em operação:

- **Ratchet** — plataforma de diagnóstico automatizado de chamados de suporte:
  <https://myratchet.com>
- **MecArts** — marketplace de engenharia com processamento tridimensional

As afirmações do TCC sobre esses projetos apoiam-se em histórico de commits,
métricas de repositório e arquivos de configuração. Um pesquisador sem acesso a
esses repositórios não pode auditá-las de forma independente — limitação
registrada na seção de Ameaças à Validade do trabalho.

---

## Licença

Código: MIT (ver `LICENSE`).
Dados (ideias, prompts, resultados, avaliações): CC BY 4.0.

Ao reutilizar, cite o trabalho e indique a versão do modelo empregada — os
resultados não são comparáveis entre modelos diferentes.
