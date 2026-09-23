# Compliance Freelancer Marketplace

Marketplace de freelancers especializados em compliance regulatório, construído com **FastAPI** seguindo estritamente a **Clean Architecture** de Robert C. Martin.

---

## Arquitetura

```
entities/          ← Camada 1: Regras de negócio (núcleo)
use_cases/         ← Camada 2: Casos de uso (regras da aplicação)
adapters/          ← Camada 3: Adaptadores de interface
frameworks/        ← Camada 4: Frameworks e drivers (periferia)
```

A **Regra de Dependência** é inviolável: dependências só apontam para dentro. Entidades não sabem que FastAPI existe. Casos de uso não sabem que SQLAlchemy existe.

---

## Camadas em detalhe

### `entities/` — Regras de Negócio

Objetos de domínio puros em Python (`@dataclass`), **zero dependências externas**.

| Entidade | Responsabilidade |
|---|---|
| `Freelancer` | Validação de dados, cálculo de rating, desativação |
| `Client` | Validação de dados corporativos |
| `Project` | Máquina de estados (OPEN → IN_PROGRESS → COMPLETED) |
| `Proposal` | Máquina de estados (PENDING → ACCEPTED/REJECTED/WITHDRAWN) |
| `Contract` | Formalização do acordo após proposta aceita |

**Decisão:** As regras como "não se pode aceitar uma proposta se o projeto não está OPEN" ou "um freelancer deve ter pelo menos uma especialização" vivem nas entidades — não nos controllers nem no banco.

### `use_cases/` — Regras da Aplicação

Orquestram entidades e definem **o que o sistema faz**, sem saber *como* persiste ou *como* é chamado.

**Ports (`use_cases/ports/repositories.py`):** Interfaces abstratas (ABCs) que definem o contrato que os repositórios devem cumprir. Os casos de uso dependem dessas abstrações, nunca de implementações concretas — isso é o *Princípio da Inversão de Dependência*.

Exemplo de fluxo complexo — `AcceptProposal`:
1. Valida que a proposta existe e está PENDING
2. Valida que o solicitante é o dono do projeto
3. Rejeita todas as demais propostas pendentes
4. Muda o status do projeto para IN_PROGRESS
5. Cria o contrato

Toda essa lógica está no caso de uso, **independente de FastAPI ou SQLAlchemy**.

### `adapters/` — Adaptadores de Interface

Fazem a ponte entre o mundo externo e os casos de uso.

- **`controllers/`**: Recebem dados da web (Pydantic schemas), chamam casos de uso com Input objects, convertem entidades em Response schemas. São o único lugar que conhece tanto o formato HTTP quanto o domínio.
- **`presenters/schemas.py`**: Schemas Pydantic para validação de entrada e serialização de saída. **Decisão:** Pydantic fica aqui, não nas entidades — entidades são Python puro, independentes de qualquer framework de validação.
- **`repositories/`**: Implementações SQLAlchemy dos contratos definidos nos ports. Fazem o mapeamento bidirecional entre ORM models e entidades de domínio (`_to_entity`). Os ORM models (`orm_models.py`) vivem aqui porque são adaptadores entre o banco e o domínio.

### `frameworks/` — Frameworks e Drivers

Camada mais externa. Contém toda a configuração de infraestrutura.

- **`database/session.py`**: Cria o engine SQLAlchemy, a session factory e expõe `get_db()` para injeção de dependência via FastAPI. Chama `Base.metadata.create_all` no startup.
- **`web/app.py`**: Instancia o `FastAPI`, registra os routers, configura o lifespan.
- **`web/dependencies.py`**: **Composition Root** — único lugar onde todas as dependências são instanciadas e conectadas. Cria repositórios, injeta nos casos de uso, injeta nos controllers. Nenhuma outra camada conhece as implementações concretas.
- **`web/routes/`**: Apenas declaram endpoints HTTP e delegam ao controller correspondente via `Depends`.

---

## Fluxo de uma requisição

```
HTTP Request
    ↓
frameworks/web/routes/  (FastAPI endpoint)
    ↓
frameworks/web/dependencies.py  (Composition Root)
    ↓
adapters/controllers/  (converte schema → input, entidade → response)
    ↓
use_cases/  (lógica de aplicação, usa ports abstratos)
    ↓
entities/  (regras de negócio puras)
    ↑
adapters/repositories/  (implementa ports, mapeia ORM ↔ entidade)
    ↑
frameworks/database/  (SQLAlchemy engine + session)
```

---

## Áreas de compliance suportadas

`LGPD`, `GDPR`, `SOX`, `ISO_27001`, `PCI_DSS`, `BACEN`, `CVM`, `HIPAA`, `COBIT`, `FEBRABAN`

---

## Como executar

```bash
pip install -r requirements.txt
python main.py
```

Acesse a documentação interativa em `http://localhost:8000/docs`.

---

## Testabilidade

Como os casos de uso dependem apenas de interfaces abstratas (ports), é possível testar toda a lógica de negócio substituindo os repositórios por implementações in-memory:

```python
class InMemoryFreelancerRepository(FreelancerRepository):
    def __init__(self):
        self._store = {}

    def save(self, freelancer):
        self._store[freelancer.id] = freelancer
        return freelancer

    def find_by_email(self, email):
        return next((f for f in self._store.values() if f.email == email), None)
    # ...

def test_create_freelancer_duplicate_email():
    repo = InMemoryFreelancerRepository()
    uc = CreateFreelancer(repo)
    uc.execute(CreateFreelancerInput("Ana", "ana@x.com", ["LGPD"], 150.0, "Especialista LGPD"))
    with pytest.raises(ValueError, match="already registered"):
        uc.execute(CreateFreelancerInput("Ana 2", "ana@x.com", ["GDPR"], 200.0, "Outro bio aqui"))
```

Nenhuma linha de FastAPI ou SQLAlchemy precisa ser carregada para testar a regra de negócio.