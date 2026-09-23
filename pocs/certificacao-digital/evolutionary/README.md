# CertChain — Plataforma de Certificação Digital

Emissão e verificação pública de certificados digitais para cursos livres.
Cada certificado possui um hash **HMAC-SHA256** único verificável sem autenticação.

---

## Decisões de Evolutionary Architecture

Este projeto segue os princípios de **Evolutionary Architecture** (Neal Ford, Rebecca Parsons).
Cada decisão técnica é anotada com sua justificativa e ponto de evolução.

### Fitness Functions

As fitness functions em `fitness/` são **testes arquiteturais** executados no CI.
Elas falham o build quando o sistema evolui de forma a violar uma característica protegida.

| Arquivo | Característica protegida | Threshold |
|---|---|---|
| `test_coupling.py` | Acoplamento bounded | ≤ 5 imports internos por módulo |
| `test_modularity.py` | Direção de dependências | Domain nunca importa de API/Services |
| `test_performance.py` | SLA de resposta | Endpoints críticos < 200ms |
| `test_security.py` | PII, autenticação, integridade | Invariantes de segurança |

> **Regra:** ao adicionar uma nova característica arquitetural relevante,
> escreva a fitness function **antes** de implementar o código.

---

### Decisões e Pontos de Evolução (Last Responsible Moment)

| Decisão | Escolha atual | Quando evoluir | Como evoluir |
|---|---|---|---|
| Banco de dados | SQLite | Concorrência real / múltiplas instâncias | Alterar `DATABASE_URL` — zero mudança de código |
| Autenticação | API Key via header | Múltiplas organizações ou papéis | Substituir `_require_api_key` por dep OAuth2/JWT |
| Hash de certificado | HMAC-SHA256 | Nunca trocar sem migrar hashes existentes | Script de migração + período de grace |
| Deploy | Uvicorn direto | Escala horizontal necessária | Adicionar Gunicorn/container sem mudar src/ |
| Schema PII | Email fora da resposta pública | Nunca — é requisito legal | N/A |

---

### Direção de Dependências

```
┌─────────────────────────────────────────┐
│  src/api/routes/          (entrada HTTP) │
│     ↓ usa                               │
│  src/services/            (orquestração) │
│     ↓ usa          ↑ nunca              │
│  src/domain/              (modelos/schemas)│
│     ↑ usa          ↑ usa               │
│  src/infrastructure/      (DB, hashing) │
└─────────────────────────────────────────┘
```

Qualquer PR que inverta uma seta **falha** `fitness/test_modularity.py`.

---

### Mudança Incremental Guiada

Fluxo para adicionar uma nova feature:

1. Escreva ou atualize a fitness function que protege a característica
2. Implemente no layer correto seguindo a direção de dependências
3. Execute `pytest fitness/ -v` — todos devem passar
4. Se uma fitness function falhar, refatore (não aumente o threshold sem decisão explícita)

---

## Estrutura

```
certchain/
├── main.py                     # Ponto de entrada FastAPI + lifespan
├── requirements.txt
├── pytest.ini
├── src/
│   ├── api/routes/
│   │   ├── courses.py          # CRUD de cursos (protegido por API key)
│   │   ├── certificates.py     # Emissão e revogação (protegido por API key)
│   │   └── verification.py     # Verificação pública (sem auth)
│   ├── domain/
│   │   ├── models.py           # Modelos SQLAlchemy: Course, Certificate
│   │   └── schemas.py          # Schemas Pydantic para I/O
│   ├── services/
│   │   ├── certificate_service.py   # Lógica de emissão e revogação
│   │   └── verification_service.py  # Lógica de verificação pública
│   └── infrastructure/
│       ├── database.py         # Engine SQLAlchemy + get_db + init_db
│       └── hash_service.py     # HMAC-SHA256 (geração e verificação)
└── fitness/
    ├── conftest.py             # Fixtures de teste (DB em memória, client, dados)
    ├── test_coupling.py        # FF: acoplamento bounded
    ├── test_modularity.py      # FF: direção de dependências
    ├── test_performance.py     # FF: SLA de resposta
    └── test_security.py        # FF: PII, auth, integridade de hash
```

---

## Instalação e execução

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Configuração via variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./certifications.db` | URL do banco — compatível com PostgreSQL |
| `CERT_SECRET_KEY` | `dev-only-change-in-production` | Secret HMAC dos certificados |
| `API_KEY` | `dev-api-key-change-in-production` | Chave para operações de escrita |

## Executar fitness functions

```bash
pytest fitness/ -v
```

---

## Endpoints

### Públicos (sem autenticação)

| Método | Path | Descrição |
|---|---|---|
| `GET` | `/verify/{hash}` | Verifica autenticidade de um certificado |
| `GET` | `/courses/` | Lista cursos ativos |
| `GET` | `/courses/{id}` | Detalhes de um curso |
| `GET` | `/health` | Health check |

### Protegidos (requer `x-api-key` header)

| Método | Path | Descrição |
|---|---|---|
| `POST` | `/courses/` | Cria curso |
| `POST` | `/certificates/` | Emite certificado |
| `GET` | `/certificates/{id}` | Consulta certificado (com email) |
| `DELETE` | `/certificates/{id}` | Revoga certificado |

---

## Exemplo de verificação pública

```bash
# Emitir certificado
curl -X POST http://localhost:8000/certificates/ \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"course_id":"<id>","recipient_name":"Maria","recipient_email":"maria@ex.com"}'

# Verificar publicamente (sem autenticação, sem expor email)
curl http://localhost:8000/verify/<verification_hash>