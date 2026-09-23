# Plataforma de Certificação Digital de Cursos Livres

API REST para emissão, revogação e **verificação pública** de certificados digitais, construída com FastAPI seguindo estritamente a **Clean Architecture** de Robert C. Martin.

---

## Estrutura de camadas

```
entities/          ← Camada 1 — Regras de negócio
use_cases/         ← Camada 2 — Casos de uso
  ports/           ← Interfaces (portas) para repositórios
adapters/          ← Camada 3 — Interface Adapters
  controllers/
  presenters/
  schemas/
frameworks/        ← Camada 4 — Frameworks & Drivers
  db/
  repositories/
  http/
main.py
```

---

## Regra de dependência

As setas de dependência apontam **exclusivamente para dentro**:

```
frameworks → adapters → use_cases → entities
```

- `entities` não importa nada do projeto.
- `use_cases` importa apenas `entities` e as interfaces abstratas em `use_cases/ports/`.
- `adapters` importa `entities`, `use_cases` e as interfaces de `ports/`.
- `frameworks` importa `adapters` e `use_cases` para realizar a injeção de dependência concreta.

---

## Decisões de Clean Architecture

### 1. Entities (`entities/`)

Dataclasses Python puras — sem dependência de framework, ORM ou Pydantic.

- `Certificate`: gera o `verification_hash` (SHA-256) em `__post_init__`. Quando reconstruído do banco, o hash existente é passado e **não é regerado**.
- `Student`: valida e-mail por regex na própria entidade — a regra de negócio não vaza para adaptadores.
- `Issuer`: normaliza CPF/CNPJ (remove pontuação) e valida comprimento na entidade.
- `Course`: garante que `workload_hours > 0` e que `name` não seja vazio.

### 2. Use Cases (`use_cases/`)

Cada caso de uso é uma classe com um único método `execute(input) → output`. Usam **Input/Output dataclasses** em vez de tipos primitivos soltos — contratos explícitos sem acoplamento ao HTTP.

| Caso de uso | Regra principal |
|---|---|
| `RegisterIssuerUseCase` | Documento único por emissor |
| `RegisterCourseUseCase` | Emissor deve existir |
| `RegisterStudentUseCase` | E-mail único |
| `IssueCertificateUseCase` | Emissor deve ser dono do curso |
| `VerifyCertificateUseCase` | Busca pública por hash; retorna `is_valid=false` se não encontrado |
| `RevokeCertificateUseCase` | Apenas o emissor original pode revogar |
| `ListStudentCertificatesUseCase` | Aluno deve existir |

#### Ports (`use_cases/ports/`)

Interfaces abstratas (`ABC`) que definem o contrato dos repositórios. Os casos de uso dependem dessas abstrações — nunca de SQLAlchemy ou qualquer banco concreto. Isso permite trocar SQLite por PostgreSQL ou MongoDB **sem tocar em nenhum caso de uso**.

### 3. Interface Adapters (`adapters/`)

- **Controllers**: recebem schemas Pydantic validados, convertem para Input do caso de uso, devolvem o Output ao presenter. São classes Python puras — não importam FastAPI.
- **Presenters**: convertem entidades de domínio em schemas de resposta Pydantic. Isolam a formatação de saída.
- **Schemas**: modelos Pydantic para validação de entrada (`Request`) e serialização de saída (`Response`). Pydantic vive aqui porque é uma biblioteca de validação de dados, não um framework web.

### 4. Frameworks & Drivers (`frameworks/`)

- **`frameworks/db/models.py`**: modelos SQLAlchemy mapeiam tabelas relacionais. UUIDs são armazenados como `String` (compatível com SQLite e PostgreSQL).
- **`frameworks/repositories/`**: implementações concretas das interfaces de `use_cases/ports/`. O método `_to_entity` reconstrói a entidade de domínio a partir do modelo ORM sem acionar efeitos colaterais indesejados.
- **`frameworks/http/dependencies.py`**: ponto de **composição** (Composition Root). É o único lugar onde os repositórios concretos são instanciados e injetados nos casos de uso e controladores via `fastapi.Depends`.
- **`frameworks/http/routers/`**: roteadores FastAPI finos — apenas recebem a requisição HTTP, delegam ao controller e mapeiam `ValueError` para `HTTPException`. Toda lógica está nos casos de uso.

---

## Como executar

```bash
pip install -r requirements.txt
python main.py
# Acesse http://localhost:8000/docs
```

### Variável de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./certifica.db` | URL de conexão SQLAlchemy |

Para PostgreSQL: `DATABASE_URL=postgresql://user:pass@host/db`

---

## Fluxo típico

```
POST /issuers          → registra emissor (instituição)
POST /courses          → cria curso vinculado ao emissor
POST /students         → registra aluno
POST /certificates     → emite certificado (emissor + aluno + curso)
GET  /certificates/verify/{hash}  → verificação pública (sem auth)
PATCH /certificates/{id}/revoke   → revogação pelo emissor
GET  /certificates/student/{id}   → histórico do aluno
```

---

## Substituindo o banco de dados

Basta criar uma nova implementação das interfaces em `use_cases/ports/` e registrá-la em `frameworks/http/dependencies.py`. Nenhuma linha de `entities/` ou `use_cases/` precisa ser alterada — essa é a garantia da Clean Architecture.