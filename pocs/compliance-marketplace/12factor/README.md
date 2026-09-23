# Compliance Freelancer Marketplace

Marketplace de freelancers especializados em compliance regulatório (LGPD, SOX, ISO 27001, PCI-DSS, BACEN, CVM, GDPR, HIPAA).

---

## Decisões 12-Factor App

### I. Base de Código
Um único repositório Git. Múltiplos deploys (dev, staging, prod) derivam da mesma base — diferenciados exclusivamente por variáveis de ambiente.

### II. Dependências
Todas as dependências declaradas em `requirements.txt` com versões fixadas. Nenhuma dependência implícita do sistema operacional é assumida. Ambientes isolados via `venv` ou contêiner.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### III. Configuração
**Zero configuração no código.** Toda config sensível ou que varia entre ambientes vive em variáveis de ambiente:

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | DSN completo do banco de dados |
| `REDIS_URL` | DSN do Redis |
| `SECRET_KEY` | Chave de assinatura JWT |
| `EMAIL_SERVICE_URL` | Endpoint do serviço de e-mail |
| `STORAGE_BUCKET_URL` | URL do bucket de armazenamento |

Copie `.env.example` → `.env` localmente. Em produção, injete via secrets manager ou variáveis da plataforma. **Nunca comite `.env`.**

### IV. Serviços de Apoio
Banco de dados, Redis e serviços externos são **recursos anexados** — acessados exclusivamente via URL de ambiente. Trocar PostgreSQL local por RDS em produção é apenas mudar `DATABASE_URL`. O código não distingue "local" de "terceiro".

### V. Build, Release, Execução
- **Build:** `pip install -r requirements.txt` — artefato imutável
- **Release:** `alembic upgrade head` — declarado no `Procfile` como processo `release`
- **Run:** `uvicorn main:app` — estágio de execução sem modificar o build

### VI. Processos
A aplicação é **completamente stateless**. Nenhum dado de sessão, cache ou upload é armazenado localmente em disco ou memória entre requisições. Estado reside exclusivamente em backing services (PostgreSQL, Redis). Qualquer instância pode ser substituída sem perda de dados.

### VII. Port Binding
FastAPI exporta HTTP via binding de porta — sem dependência de servidor de aplicação externo. `PORT` é injetado por variável de ambiente.

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### VIII. Concorrência
Escala horizontal via modelo de processos declarado no `Procfile`:

```
web:    uvicorn (múltiplos workers via WEB_CONCURRENCY)
worker: processamento assíncrono de tarefas
```

Adicionar capacidade = aumentar instâncias do processo `web`. Sem threads compartilhadas.

### IX. Descartabilidade
- **Startup rápido:** inicialização assíncrona sem bloqueio
- **Shutdown gracioso:** `on_event("shutdown")` libera conexões de banco e encerra workers limpos
- **SIGTERM handling:** uvicorn respeita sinais do sistema operacional

### X. Paridade Dev/Prod
- Mesmo banco (PostgreSQL) em todos os ambientes via Docker Compose localmente
- Mesma imagem de contêiner promovida de dev → staging → prod
- `DEBUG=false` em produção desativa docs automáticos (`/docs`, `/redoc`)

```bash
# Dev local — mesma stack de produção
docker compose up -d postgres redis
```

### XI. Logs
Logs são **streams de eventos** escritos em `stdout`. Nenhum arquivo de log é gerenciado pela aplicação. A plataforma (ECS, Kubernetes, Heroku) é responsável por coletar, rotacionar e agregar.

```python
logging.basicConfig(stream=sys.stdout, level=settings.LOG_LEVEL, ...)
```

### XII. Processos Administrativos
Migrações de banco são processos one-off executados no mesmo ambiente e release da aplicação:

```bash
# Executado automaticamente no Procfile como processo 'release'
alembic upgrade head

# Ou manualmente como tarefa administrativa
alembic revision --autogenerate -m "add freelancer skills"
```

---

## Rodando Localmente

```bash
# 1. Dependências
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configuração
cp .env.example .env
# Edite .env com seus valores locais

# 3. Backing services
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:16
docker run -d -p 6379:6379 redis:7

# 4. Migração (processo release)
alembic upgrade head

# 5. Aplicação (processo web)
uvicorn main:app --reload --port 8000
```

## Estrutura

```
.
├── main.py                  # Entry point — vincula factory ao uvicorn
├── Procfile                 # Modelo de processos (web, worker, release)
├── requirements.txt         # Dependências declaradas
├── .env.example             # Contrato de configuração — sem valores reais
├── alembic.ini              # Config de migrations (lê DATABASE_URL do env)
├── migrations/
│   └── env.py               # Runner de migrations assíncrono
└── app/
    ├── config.py            # Leitura de env vars via pydantic-settings
    ├── factory.py           # Application factory com lifecycle hooks
    ├── database.py          # Engine assíncrona como backing service
    ├── models.py            # Modelos SQLAlchemy
    ├── schemas.py           # Schemas Pydantic (I/O)
    ├── dependencies.py      # Injeção de dependências (auth)
    └── routers/
        ├── health.py        # Health check (verifica backing service)
        ├── auth.py          # JWT token endpoint
        ├── freelancers.py   # CRUD de freelancers
        └── projects.py      # CRUD de projetos + assign