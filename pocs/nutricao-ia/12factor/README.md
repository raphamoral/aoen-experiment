# NutriAI — Nutrição Personalizada com IA

App de nutrição personalizada que analisa exames laboratoriais via IA (Claude) e gera recomendações nutricionais baseadas em evidências.

---

## Decisões 12-Factor App

### I. Codebase
Um único repositório Git. Múltiplos deploys (dev/staging/prod) são obtidos variando **apenas as env vars**, nunca o código.

### II. Dependências
Todas as dependências estão declaradas explicitamente em `requirements.txt`. Nenhuma biblioteca do sistema é assumida. Instalação isolada via virtualenv.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### III. Config
**Zero configuração hard-coded.** Toda config sensível ou que varia por ambiente (banco, chaves de API, secrets) é lida de variáveis de ambiente via `pydantic-settings` (`app/config.py`).

```bash
cp .env.example .env
# edite .env com seus valores
```

### IV. Backing Services
PostgreSQL, Redis e Anthropic Claude são tratados como **recursos anexados** — conectados via URL/chave de ambiente. Podem ser substituídos (ex: RDS → Aurora, Redis local → ElastiCache) sem alterar código.

| Serviço     | Var de ambiente    | Papel                        |
|-------------|--------------------|------------------------------|
| PostgreSQL  | `DATABASE_URL`     | Persistência de dados         |
| Redis       | `REDIS_URL`        | Cache de recomendações        |
| Anthropic   | `ANTHROPIC_API_KEY`| Análise de IA dos exames      |

### V. Build, Release, Run
- **Build:** `pip install -r requirements.txt`
- **Release:** `alembic upgrade head` (via `Procfile` `release:`)
- **Run:** `gunicorn` via `Procfile` `web:`

### VI. Processos (Stateless)
A aplicação **não armazena nenhum estado em memória** entre requests. Sessões de DB são criadas e destruídas por request. Cache vai para Redis. Múltiplas instâncias podem rodar em paralelo sem conflito.

### VII. Port Binding
A aplicação é self-contained e exporta HTTP via `uvicorn`/`gunicorn`. Não depende de servidor web externo injetado (ex: Apache).

```bash
APP_PORT=8000 gunicorn main:app -k uvicorn.workers.UvicornWorker
```

### VIII. Concorrência
Escalabilidade horizontal via processos Gunicorn. Para aumentar throughput: suba `APP_WORKERS` ou adicione instâncias do processo `web`.

```
web: gunicorn main:app -w ${APP_WORKERS:-2} -k uvicorn.workers.UvicornWorker
```

### IX. Descartabilidade
- **Startup rápido:** sem aquecimento de cache em memória local.
- **Shutdown gracioso:** `--graceful-timeout 30` no Gunicorn; `lifespan` do FastAPI fecha conexões DB.

### X. Dev/Prod Parity
- Mesmas dependências em todos os ambientes (`requirements.txt` fixado com versões exatas).
- Mesmos serviços (PostgreSQL, Redis) — sem SQLite em dev ou mock de Redis.
- `APP_ENV` controla apenas comportamentos de debug (ex: desabilitar `/docs` em prod).

### XI. Logs
A aplicação **nunca gerencia arquivos de log**. Todos os logs vão para `stdout` via `structlog` em formato JSON. O ambiente (Docker, Heroku, Kubernetes) é responsável por capturar e rotear.

```bash
LOG_LEVEL=DEBUG LOG_FORMAT=json uvicorn main:app
```

### XII. Processos Admin
Migrações de banco são one-off processes, não acopladas ao runtime:

```bash
# Localmente
alembic upgrade head

# Em produção (Heroku/Railway/Render)
# Executado automaticamente via Procfile `release:` antes do deploy
```

---

## Rodando localmente

```bash
# 1. Infraestrutura (backing services)
docker run -d -p 5432:5432 -e POSTGRES_DB=nutrition_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password postgres:16
docker run -d -p 6379:6379 redis:7

# 2. App
cp .env.example .env        # preencha ANTHROPIC_API_KEY
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload   # Factor VII: porta via env APP_PORT
```

Acesse: `http://localhost:8000/docs`

---

## Estrutura

```
├── app/
│   ├── config.py              # Factor III: settings via env
│   ├── database.py            # Factor IV: PostgreSQL backing service
│   ├── cache.py               # Factor IV: Redis backing service
│   ├── models.py              # SQLAlchemy ORM
│   ├── schemas.py             # Pydantic I/O schemas
│   ├── dependencies.py        # FastAPI DI (auth, db session)
│   ├── logging_config.py      # Factor XI: stdout JSON logs
│   ├── routers/
│   │   ├── users.py           # Auth endpoints
│   │   ├── exams.py           # Lab exam endpoints
│   │   └── nutrition.py       # AI recommendation endpoints
│   └── services/
│       ├── auth_service.py    # JWT auth logic
│       ├── ai_service.py      # Factor IV: Claude AI integration
│       ├── exam_service.py    # Exam business logic
│       └── nutrition_service.py # Recommendation + cache logic
├── migrations/                # Alembic (Factor XII: admin process)
├── main.py                    # Factor VII: port binding entry point
├── Procfile                   # Factor VI/VIII: process model
├── requirements.txt           # Factor II: explicit deps
└── .env.example               # Factor III: config template