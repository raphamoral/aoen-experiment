# Compliance Freelancer Marketplace

Marketplace de freelancers especializados em compliance regulatório (LGPD, GDPR, SOX, PCI-DSS, ISO 27001, BACEN, CVM, SUSEP, HIPAA).

Construído seguindo os princípios de **Evolutionary Architecture** (Neal Ford, Rebecca Parsons, Patrick Kua).

---

## Princípios Aplicados

### 1. Fitness Functions

O diretório `fitness/` contém testes arquiteturais automatizados que validam atributos de qualidade contínuamente no CI:

| Fitness Function | Arquivo | O que valida |
|---|---|---|
| Acoplamento entre camadas | `test_architecture_coupling.py` | Domain não importa infra/framework |
| Imutabilidade do audit trail | `test_audit_immutability.py` | AuditRepository nunca expõe delete/update |
| Segurança de dados | `test_security_fitness.py` | Sem segredos hardcoded, Pydantic em todas as rotas |
| Performance | `test_performance_fitness.py` | Funções async, complexidade ciclomática ≤ 10 |
| Evolvabilidade | `test_evolvability_fitness.py` | API versionada, DI em serviços, domínio puro |

```bash
# Rodar todas as fitness functions
pytest fitness/ -v
```

### 2. Decisões Reversíveis (ADRs)

#### ADR-001: Configuração via Pydantic BaseSettings
**Decisão:** variáveis de ambiente com fallback para `.env`.
**Reversibilidade:** troca para AWS SSM, Vault ou Azure Key Vault mudando apenas `src/config.py`, sem impacto no domínio.

#### ADR-002: Domínio Puro (Plain Dataclasses)
**Decisão:** `src/domain/models.py` usa apenas stdlib Python — sem ORM, sem Pydantic, sem FastAPI.
**Reversibilidade:** permite adotar Event Sourcing, CQRS ou qualquer framework futuro sem reescrever regras de negócio.

#### ADR-003: Audit Trail Append-Only
**Decisão:** `AuditRepository` expõe apenas `record()` e `find_by_entity()`.
**Motivação:** LGPD Art. 37, SOX Section 802 e PCI DSS Req. 10.5 exigem logs imutáveis. A fitness function garante que isso nunca seja violado acidentalmente.

#### ADR-004: SQLite em Desenvolvimento, PostgreSQL em Produção
**Decisão:** `DATABASE_URL` externalizado. SQLite para onboarding rápido.
**Reversibilidade:** `aiosqlite` → `asyncpg` mudando apenas a env var.

#### ADR-005: Repository Pattern como Seam de Evolução
**Decisão:** serviços recebem repositórios via injeção de dependência.
**Reversibilidade:** persistence layer pode evoluir para DynamoDB, Elasticsearch ou Event Store sem afetar serviços ou domínio.

#### ADR-006: Anti-Corruption Layer na Borda da API
**Decisão:** `src/api/v1/schemas.py` (Pydantic) é separado de `src/domain/models.py` (dataclasses).
**Motivação:** contratos de API e modelos de domínio evoluem em ritmos diferentes.

### 3. Mudança Incremental Guiada

A estrutura modular atual é um **monólito modular** — os bounded contexts estão organizados por pasta mas compartilham o mesmo processo.

**Caminho de evolução incremental definido:**

```
Fase 1 (atual): Monólito modular
  src/domain, src/services, src/infrastructure, src/api

Fase 2 (se escala exigir): Separar em pacotes Python independentes
  packages/freelancers/, packages/projects/, packages/proposals/

Fase 3 (se bounded contexts precisarem de SLAs diferentes): Microserviços
  Cada pacote vira um serviço FastAPI independente
  Comunicação via eventos (Kafka/SQS) — audit trail vira event log
```

A fitness function `test_evolvability_fitness.py` garante que cada fase seja possível sem reescrita.

### 4. Last Responsible Moment

Decisões deliberadamente postergadas:

| Decisão | Por quê postergar |
|---|---|
| Autenticação/JWT | Requisitos de tenant isolation não foram validados ainda |
| Rate limiting | Volume de usuários desconhecido |
| Caching (Redis) | Sem métricas de produção para identificar hot paths |
| Busca full-text (Elasticsearch) | Catálogo pequeno — SQL `LIKE` é suficiente hoje |
| Fila de jobs (Celery) | Nenhum processo assíncrono identificado ainda |

Cada uma dessas decisões tem um **seam arquitetural** preparado (repositórios, configuração externalizada, domínio puro) que permite adotá-las quando — e só quando — a evidência justificar.

---

## Estrutura do Projeto

```
.
├── main.py                          # Entrypoint
├── requirements.txt
├── src/
│   ├── app.py                       # Application factory
│   ├── config.py                    # Configuração externalizada (ADR-001)
│   ├── domain/
│   │   └── models.py                # Domínio puro, zero dependências (ADR-002)
│   ├── infrastructure/
│   │   ├── database.py              # Engine SQLAlchemy async (ADR-004)
│   │   ├── orm_models.py            # Mapeamento ORM separado do domínio
│   │   └── repositories.py         # Seam de persistência (ADR-005)
│   ├── services/
│   │   ├── freelancer_service.py    # Orquestração de casos de uso
│   │   ├── project_service.py
│   │   └── proposal_service.py
│   └── api/
│       └── v1/
│           ├── router.py            # API versionada (ADR-006)
│           ├── schemas.py           # Contratos de API (Pydantic)
│           ├── freelancers.py
│           ├── projects.py
│           ├── proposals.py
│           └── health.py
└── fitness/                         # Fitness functions arquiteturais
    ├── conftest.py
    ├── test_architecture_coupling.py
    ├── test_audit_immutability.py
    ├── test_security_fitness.py
    ├── test_performance_fitness.py
    └── test_evolvability_fitness.py
```

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Rodar a aplicação
uvicorn main:app --reload

# Rodar fitness functions (CI obrigatório)
pytest fitness/ -v --tb=short

# Rodar com cobertura
pytest fitness/ src/ --cov=src --cov-report=term-missing
```

---

## Áreas de Compliance Suportadas

`GDPR` · `LGPD` · `SOX` · `PCI_DSS` · `ISO_27001` · `HIPAA` · `BACEN` · `CVM` · `SUSEP`