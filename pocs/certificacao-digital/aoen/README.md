# CertChain — Plataforma de Certificação Digital de Cursos Livres

Plataforma multi-tenant para emissão e verificação pública de certificados digitais,
construída segundo o **framework AOEN**.

---

## Decisões AOEN

### Fase 1 — NÚCLEO (VALOR)
**Core diferenciador:** assinatura criptográfica Ed25519 + hash canônico determinístico.

O valor central do produto não é "emitir PDFs" — é **provar autenticidade sem depender
de nenhum terceiro**. Qualquer pessoa com a chave pública do emissor pode verificar um
certificado offline, para sempre, mesmo que a plataforma deixe de existir.

Isolamento aplicado:
- `core/signing.py` — zero dependências externas (só `cryptography`)
- `core/hash_chain.py` — serialização canônica; qualquer implementação que siga o contrato
  pode re-verificar o hash
- `core/qr_generator.py` — interface física do certificado

A **Service Layer** (`services/`) orquestra o core sem conhecer FastAPI ou HTTP.
Pode ser chamada por CLI, Celery worker, ou outro microsserviço sem alteração.

### Fase 2 — MULTI-INTERFACE (ALCANCE)
Três interfaces sobre a mesma lógica:

| Interface | Arquivo | Mercado |
|---|---|---|
| REST API autenticada | `routers/certificates.py` | Integração B2B / LMS |
| Endpoint público `/verify/{id}` | `routers/verification.py` | Empregadores, validadores |
| QR Code em PNG/base64 | `core/qr_generator.py` | Certificados físicos/PDF |

O router de verificação é montado **fora** do prefixo `/api/v1` para gerar URLs
limpas e compartilháveis.

### Fase 3 — CONFIG-DRIVEN (ESCALA)
O fluxo de certificação é **idêntico** para todos os clientes.
O que muda são parâmetros em `TenantConfig` (config.py):

```python
TenantConfig.DEFAULTS = {
    "certificate_template": "default",
    "primary_color": "#1a3a5c",
    "validity_years": 2,
    "max_certificates_per_month": 100,
    "issuer_name": "CertChain",
    ...
}
```

Onboarding de um novo cliente = criar um registro `Tenant` com JSON de config.
**Nenhuma linha de código é alterada.**

### Fase 4 — ISOLAMENTO (CUSTO)
Cada tenant tem:
- **Par de chaves Ed25519 próprio** — comprometimento de um tenant não afeta outros
- **Limite mensal de certificados** — custo de infraestrutura mensurável por cliente
- **`VerificationLog`** — cada verificação pública é registrada com `tenant_id`,
  permitindo cobrar pelo uso real (modelo usage-based billing)

A abstração `PrivateKeyStore` (services/certificate_service.py) permite substituir
o armazenamento em memória por **HashiCorp Vault** ou **AWS KMS** em produção
sem alterar nenhum outro arquivo.

---

## Estrutura

```
.
├── main.py                    # Ponto de entrada — apenas montagem
├── config.py                  # Settings globais + TenantConfig
├── database.py                # Engine SQLAlchemy + get_db
├── models.py                  # Tenant, Course, Certificate, VerificationLog
├── core/
│   ├── signing.py             # Ed25519 generate/sign/verify
│   ├── hash_chain.py          # Payload canônico + SHA-256
│   └── qr_generator.py        # QR Code para URL de verificação
├── services/
│   ├── certificate_service.py # Emissão, revogação, listagem
│   ├── verification_service.py# Verificação pública com log
│   └── tenant_service.py      # Onboarding + config de tenants
└── routers/
    ├── tenants.py             # POST/GET /api/v1/tenants
    ├── courses.py             # POST/GET /api/v1/courses
    ├── certificates.py        # POST/GET /api/v1/certificates
    └── verification.py        # GET /verify/{public_id} (público)
```

## Instalação

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Acesse `http://localhost:8000/docs` para o Swagger UI.

## Fluxo básico

```bash
# 1. Criar tenant
POST /api/v1/tenants
{"slug": "escola-alpha", "name": "Escola Alpha"}
# → retorna private_key_pem (guarde em segurança; nunca mais exposto)

# 2. Criar curso
POST /api/v1/courses
{"tenant_id": "...", "title": "Python para Iniciantes", "workload_hours": 40}

# 3. Emitir certificado
POST /api/v1/certificates
{"tenant_id": "...", "course_id": "...", "recipient_name": "João Silva", "recipient_email": "joao@email.com"}

# 4. Verificação pública (sem autenticação)
GET /verify/{public_id}
# → status, assinatura válida, QR code base64
```

## Evoluções previstas pelo framework

| Evolução | Impacto no código |
|---|---|
| Substituir SQLite por PostgreSQL | Apenas `DATABASE_URL` no `.env` |
| Adicionar template PDF por tenant | Novo campo em `TenantConfig.DEFAULTS` |
| Mover `core/` para microsserviço gRPC | Apenas `CertificateService._key_store` e chamadas ao core |
| Cobrar por verificação | `VerificationLog` já existe; adicionar billing no `VerificationService` |
| Interface CLI para emissão em lote | Importar e chamar `CertificateService` diretamente |