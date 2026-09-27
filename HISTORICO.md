# Histórico das rodadas

Registro cronológico do que foi executado, do que falhou e do que cada rodada
sustenta. Existe para que ninguém precise inferir a procedência dos números a
partir dos arquivos soltos no repositório.

Nenhum artefato foi removido. As rodadas incompletas continuam aqui, e as razões
pelas quais não devem ser citadas estão descritas abaixo.

---

## Abril de 2026 — rodada original

**O que se pretendia:** 100 ideias × 7 abordagens = 700 gerações e 700
avaliações, com `run_experiment.py` e o modelo pelo alias `sonnet`.

**O que de fato ocorreu:** a execução interrompeu-se por limite de uso do CLI por
volta da ideia 21. O `run_claude()` devolvia `f"ERROR: {result.stderr}"` quando o
processo saía com código diferente de zero, e o stderr vinha vazio. Esses erros
foram **gravados como artefatos**, e a retomada os tratava como trabalho
concluído, porque o critério era `if result_file.exists()`. A consolidação somou
tudo sem verificar validade.

**O que restou:** `experimento/consolidated.json` tem 700 registros, dos quais
apenas **147 contêm as nove notas** — ideias 0 a 20. Os outros 553 são
`{"scores": {"raw_response": "ERROR: "}}`. São 1.323 pontos de dados, não 6.300.

As médias publicadas em versões anteriores do trabalho (AOEN 7,31; Clean
Architecture 4,42) vieram desses 147 registros, ou seja, de 21 ideias.

**Arquivos:** `experimento/results/`, `experimento/consolidated.json`

---

## 13 de abril de 2026 — rodadas v2 e v3

Tentativas de retomada e de reformulação do desenho, também incompletas.

| Arquivo | Cobertura | Observação |
|---|---|---|
| `consolidated_v2.json` | 22 ideias × 7 | nesta rodada o Architecture for Flow (6,88) fica à frente do AOEN (6,50) |
| `consolidated_v2_full.json` | AOEN com 100 ideias, concorrentes com 22 | braços desbalanceados, não comparável |
| `consolidated_v3_specialists.json` | 10 personas de especialista avaliando por critério, 2.320 notas | desenho distinto, cobertura desigual entre braços |

A inversão do ranking na v2 é relevante e está registrada como tal: a liderança
do AOEN **não era estável** entre as rodadas incompletas.

---

## 21 de setembro de 2026 — rodada v4 (referência)

**Motivo:** os números publicados não correspondiam aos dados. A rodada foi
refeita do zero em vez de completada, porque o alias `sonnet` já não apontava
para o mesmo modelo de abril, e misturar gerações de épocas diferentes
introduziria uma variável adicional.

**O que mudou no instrumento:**

- `runner.py` substituiu `run_experiment.py`. Valida cada artefato **antes** de
  gravar; erro nunca vira arquivo. Retoma por artefato, não por contador.
- Retentativa com recuo exponencial, e distinção entre falha de conteúdo e
  esgotamento de cota. Ao esgotar a cota, para gravando checkpoint em vez de
  queimar a fila.
- Modelo fixado por identificador (`claude-sonnet-5`), nunca por alias. Cada
  artefato registra o modelo e o hash do prompt que o produziu.
- Removida a truncagem de 3.000 caracteres que o avaliador aplicava à resposta.
  Ela penalizava sistematicamente as abordagens verbosas: o Clean Architecture
  gera em média 15,6 mil caracteres, dos quais o avaliador lia 3 mil.
- A consolidação recusa-se a agregar conjunto incompleto e nomeia cada buraco.

**Resultado:** 700 gerações e 700 avaliações, **cobertura 100%**, zero artefatos
inválidos, 6.300 pontos de dados.

| Abordagem | Média |
|---|---|
| AOEN | 8,91 |
| Architecture for Flow | 8,19 |
| Evolutionary Architecture | 8,05 |
| Twelve-Factor App | 7,84 |
| Sem framework (proibição) | 7,69 |
| Hexagonal Architecture | 7,61 |
| Clean Architecture | 7,20 |

Na comparação pareada, o AOEN supera cada rival em ao menos 97 dos 100 casos.

**Percalços registrados:** a rodada parou duas vezes por limite de uso e uma vez
por queda do mount do disco onde escrevia. Em nenhum dos casos houve perda ou
corrupção de artefato — o padrão de gravar apenas após validar tornou as
interrupções inócuas. A execução foi então movida para disco local.

**Arquivos:** `experimento/results_v4/`, `experimento/consolidated_v4.json`

---

## 21 de setembro de 2026 — figuras regeradas

Ao regerar as figuras constatou-se que `all_charts_final.py` continha os valores
das séries **cravados no código**, e que esses valores não correspondiam a
nenhum arquivo consolidado do repositório. A figura de eficiência, além disso,
plotava totais dos três repositórios enquanto a tabela correspondente do trabalho
publicava a média deles — divergência de 3× sem indicação em nenhum dos dois.

As figuras passaram a ser geradas a partir de `consolidated_v4.json` e das
tabelas do próprio trabalho, por `gerar_figuras_v4.py` e
`gerar_figuras_restantes.py`. Os scripts antigos foram para `legado/`, com aviso.

---

## 27 de setembro de 2026 — estudo de simetria de esquema

**Motivo:** o prompt do AOEN exigia 17 campos de resposta, dez correspondendo a
critérios da rubrica e com exemplos de cálculo, contra 10 a 13 campos e 3 a 4
correspondências dos concorrentes. Da rodada v4 isolada não se distingue a
contribuição do framework da contribuição do formulário.

**Desenho:** nivelamento **para cima**. Cada concorrente recebeu 17 campos no
vocabulário canônico da própria fonte, mais a cauda genérica exigente do AOEN.
Dois braços de controle sem framework. 30 ideias sorteadas com semente fixa. O
braço do AOEN não foi reexecutado.

**Resultado:** 210 gerações e 210 avaliações, cobertura 100%. O formulário
responde por 1,95 ponto; o framework, por 0,11. O AOEN mantém a primeira posição
e vence os cinco frameworks em 30 de 30 ideias, mas empata praticamente com um
prompt neutro que formule as mesmas perguntas sem mencionar o framework.

Detalhamento e ressalvas em `README.md`, seção *Estudo de simetria de esquema*.

**Arquivos:** `simetria.py`, `ablacao.py`, `experimento/results_simetria/`,
`experimento/consolidated_simetria.json`

---

## O que permanece sem controle

- A rubrica foi construída pelo mesmo pesquisador que propõe o framework. Os
  nove critérios têm âncora independente na literatura, mas a seleção e a
  redação são dele.
- O avaliador recebe o nome da abordagem que gerou cada proposta: a avaliação
  não é cega.
- Gerador e avaliador são o mesmo modelo, ainda que em execuções separadas.
- O código-fonte dos dois projetos do estudo de caso não integra o repositório,
  de modo que as afirmações da primeira etapa metodológica não podem ser
  auditadas de forma independente.
