# ComplianceMatch

Marketplace de freelancers especializados em compliance regulatório.

## Decisões AOEN

### Fase 1 — NÚCLEO (VALOR)

O diferenciador está em `core/compliance_scorer.py` e `core/matching_engine.py`.

O motor de scoring avalia cinco dimensões específicas do domínio regulatório:
sobreposição de domínios (LGPD, SOX, ISO 27001, etc.), certificações exigidas
(CIPP/E, CISA, etc.), anos de experiência nos frameworks requeridos, rating
do freelancer e adequação de taxa ao orçamento. Cada dimensão tem peso
configurável por tenant.

O núcleo não importa FastAPI, SQLAlchemy ou qualquer framework. É Python
puro com dataclasses. Pode ser testado unitariamente sem banco ou HTTP,
e pode ser movido para um worker separado sem refatoração.

### Fase 2 — MULTI-INTERFACE (ALCANCE)

A Service Layer (`services/`) expõe a lógica sem acoplamento a HTTP.
Os routers (`routers/`) são finos: validam entrada, delegam para o service,
formatam saída. A mesma lógica serve uma API REST hoje e amanhã pode servir
um CLI, um SDK Python, uma interface de webhook ou uma fila de mensagens —
sem duplicar regras de negócio.

Interfaces abertas pelo design atual:
- **REST API** — os routers FastAPI
- **SDK interno** — qualquer script Python importa os services diretamente
- **Worker async** — `matching_service.run_project_matching` não tem estado HTTP,
  pode rodar em Celery/RQ/ARQ sem alteração

### Fase 3 — CONFIG-DRIVEN (ESCALA)

O fluxo de matching é fixo no código. Os parâmetros são configuráveis por
tenant via `tenant.config` (JSON no banco) que é mesclado com
`TENANT_DEFAULTS` em `config.py`. Cada tenant pode ajustar:

- `match_weights` — redistribuir o peso de cada dimensão de scoring
- `require_certification` — exigir match obrigatório de certificações
- `min_freelancer_rating` — filtrar candidatos abaixo de um patamar
- `allowed_domains` — restringir o marketplace a domínios específicos
- `max_matches_per_project` — controlar granularidade dos resultados

Adicionar um novo cliente enterprise com requisitos de compliance diferentes
(ex: setor bancário só vê domínios BACEN/CVM) não exige nova linha de código —
apenas uma entrada de config.

### Fase 4 — ISOLAMENTO (CUSTO)

`core/cost_tracker.py` é puro: recebe primitivos, devolve um `CostEvent`
com o custo calculado em créditos. Não acessa banco.

`UsageRecord` persiste cada operação com tenant_id, operação, unidades e
custo. O endpoint `/billing/usage` agrega isso por tenant. Isso permite:

- **Cobrar por uso real**: cada `match_run` consome créditos proporcionais
  ao número de freelancers avaliados
- **Medir custo por cliente**: sem instrumentação adicional
- **Isolar o processo**: o matching pode rodar em processo/container separado
  e reportar custos via evento, sem mudança no modelo de dados

## Estrutura

```
.
├── main.py                  # Composição do app FastAPI
├── database.py              # Engine e sessão SQLAlchemy
├── models.py                # Entidades ORM
├── schemas.py               # Contratos Pydantic (I/O)
├── config.py                # Settings + defaults + limites por plano
├── core/
│   ├── compliance_scorer.py # Scoring puro por dimensão regulatória
│   ├── matching_engine.py   # Orquestração do ranking de candidatos
│   └── cost_tracker.py      # Cálculo de custo por operação
├── services/
│   ├── freelancer_service.py
│   ├── project_service.py
│   ├── matching_service.py  # Ponte ORM ↔ core
│   ├── tenant_service.py
│   └── billing_service.py
└── routers/
    ├── freelancers.py
    ├── projects.py
    ├── matches.py
    └── tenants.py
```

## Execução

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# Docs em http://localhost:8000/docs
```

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./compliancematch.db` | URL do banco |
| `SECRET_KEY` | `change-me-in-production` | Chave de assinatura |
| `COST_MATCH_RUN` | `1.0` | Créditos por freelancer avaliado |
| `COST_PROJECT_OPEN` | `0.5` | Créditos por projeto aberto |
| `COST_PER_HIRE` | `5.0` | Créditos por contratação efetivada |