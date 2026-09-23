# CertificaDigital

Plataforma de certificação digital de cursos livres com verificação pública.

---

## Decisões 12-Factor

### I. Codebase — Uma base, múltiplos deploys
Um único repositório Git. Ambientes (dev, staging, prod) são deploys distintos
da mesma base, diferenciados exclusivamente por variáveis de ambiente.

### II. Dependencies — Dependências declaradas e isoladas
`requirements.txt` com versões exatas. Nenhuma dependência implícita do sistema
operacional. Use `python -m venv .venv && pip install -r requirements.txt`.

### III. Config — Configuração no ambiente
Zero configuração hardcoded. Toda variável sensível ou que muda entre ambientes
(DATABASE_URL, SECRET_KEY, ALLOWED_ORIGINS) é lida via `os.environ` através do
`pydantic-settings`. O arquivo `.env.example` documenta o contrato; `.env` real
nunca é versionado.

### IV. Backing Services — Serviços de apoio como recursos anexados
O banco de dados é tratado como recurso externo acessado via `DATABASE_URL`.
Trocar de Postgres local para RDS em produção requer apenas alterar a variável
— sem mudança de código.

### V. Build, Release, Run — Estágios separados
- **Build**: `pip install` + geração de artefato.
- **Release**: `alembic upgrade head` (declarado no `Procfile` como `release`).
- **Run**: Gunicorn inicia os workers. Nenhum estágio mistura responsabilidades.

### VI. Processes — Processos stateless
A aplicação FastAPI não armazena estado em memória entre requisições. Sem
sessões locais, sem cache em variável global, sem uploads em disco local.
Estado persistente vive exclusivamente no banco (backing service).

### VII. Port Binding — Exportar serviços via port binding
O Gunicorn se vincula a `0.0.0.0:$PORT`. A aplicação é auto-suficiente; nenhum
servidor de aplicação externo (Apache, Nginx) é necessário para funcionar.

### VIII. Concurrency — Concorrência via modelo de processos
Escalabilidade horizontal: aumente `-w` no `Procfile` ou suba mais dynos/pods.
O Gunicorn com workers `UvicornWorker` combina multiprocesso (Gunicorn) com
I/O assíncrono (Uvicorn/asyncio) sem estado compartilhado entre workers.

### IX. Disposability — Robustez com início rápido e encerramento elegante
FastAPI usa `lifespan` para setup/teardown. O Gunicorn responde a `SIGTERM`
drenando requisições em andamento antes de encerrar. Nenhum worker acumula
estado que precise ser "salvo" no shutdown.

### X. Dev/Prod Parity — Paridade entre ambientes
O mesmo `Procfile`, `requirements.txt` e imagem Docker são usados em todos os
ambientes. Diferenças entre dev e prod existem apenas nas variáveis de ambiente
(ex.: `DATABASE_URL` aponta para instâncias diferentes).

### XI. Logs — Logs como fluxo de eventos
A aplicação escreve logs estruturados **somente no stdout**. Nenhum arquivo de
log é aberto. A infraestrutura (systemd, CloudWatch, Datadog) é responsável por
capturar, rotacionar e agregar o stream.

### XII. Admin Processes — Tarefas administrativas como processos únicos
Migrações (`alembic upgrade head`) e scripts administrativos rodam como
processos one-off no mesmo ambiente/release, nunca embutidos no boot da app.

---

## Quickstart

```bash
cp .env.example .env
# edite .env com suas credenciais locais

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

alembic upgrade head               # cria as tabelas

uvicorn main:app --reload          # desenvolvimento local
```

### Emitir certificado

```bash
curl -X POST http://localhost:8000/certificates/ \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_name": "Maria Silva",
    "recipient_email": "maria@exemplo.com",
    "course_name": "Python para Dados",
    "course_hours": "40h"
  }'
```

### Verificar certificado (público, sem autenticação)

```bash
curl http://localhost:8000/verify/<verification_hash>
```

---

## Produção (exemplo Heroku/Railway/Render)

```bash
heroku config:set DATABASE_URL=postgresql://...
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set ENVIRONMENT=production
heroku config:set ALLOWED_ORIGINS=https://app.certifica.exemplo.com
git push heroku main
```

O `Procfile` cuida do `release` (migrações) e do `web` (workers) automaticamente.