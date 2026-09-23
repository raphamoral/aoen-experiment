# NutriAI — Nutrição Personalizada com IA

App de nutrição personalizada baseado em exames laboratoriais, utilizando IA para análise
de deficiências nutricionais e geração de planos alimentares personalizados.

---

## Arquitetura Evolutiva (Neal Ford, Rebecca Parsons, Patrick Kua)

Este projeto aplica os quatro princípios centrais de *Building Evolutionary Architectures*:

### 1. Fitness Functions

Testes arquiteturais automatizados que validam características do sistema a cada commit.
São executados como parte do pipeline de CI: `pytest fitness/ -v`.

| Arquivo                        | Característica validada                              |
|-------------------------------|------------------------------------------------------|
| `fitness/test_coupling.py`    | Camadas não se acoplam fora da direção permitida     |
| `fitness/test_performance.py` | Endpoints respondem dentro do SLO (500 ms)           |
| `fitness/test_security.py`    | Inputs inválidos rejeitados, headers corretos        |
| `fitness/test_modularity.py`  | Responsabilidade única, coesão, config centralizada  |

**Regra de acoplamento (fitness function guia):**
```
api → services → repositories → models
             ↑
     infrastructure (apenas repositories e services)
```

### 2. Decisões Reversíveis

| Decisão              | Estado atual (MVP)              | Como reverter                              |
|---------------------|---------------------------------|---------------------------------------------|
| Banco de dados       | SQLite (`aiosqlite`)            | Trocar `DATABASE_URL` no `.env`             |
| AI provider          | Mock / OpenAI                   | Trocar `AI_PROVIDER` no `.env`              |
| Autenticação         | Sem auth (fitness fn documenta) | Adicionar middleware JWT sem mudar services |
| Schemas Pydantic     | Inline nas routes               | Extrair para `src/schemas/` quando crescer  |
| Planos nutricionais  | JSON em coluna única            | Normalizar tabela quando queries exigirem   |

### 3. Mudança Incremental Guiada

- `BaseRepository[T]` define contrato; trocar storage não toca services
- `AIProvider` é um Protocol Python — providers são substituíveis sem alterar callers
- `get_ai_provider()` é o único ponto de decisão sobre qual IA usar
- Toda configuração em `src/config.py` — fitness function impede hardcode

### 4. Last Responsible Moment

- SQLite até validar modelo de negócio com usuários reais
- Provider mock até definir budget e qualidade de API externa
- Sem autenticação no MVP (fitness function de segurança registra a dívida e guia implementação futura)
- Schema JSON para planos nutricionais até queries complexas justificarem normalização

---

## Registro de Decisões Arquiteturais (ADR)

**ADR-001 — SQLite como banco inicial**
- *Contexto:* MVP sem usuários reais, custo operacional mínimo desejado
- *Decisão:* `sqlite+aiosqlite` via SQLAlchemy async; engine encapsulado em `infrastructure/database.py`
- *Reversão:* Definir `DATABASE_URL=postgresql+asyncpg://...` no `.env`. Zero mudança em repositories.

**ADR-002 — AI Provider como Protocol**
- *Contexto:* Mercado de modelos de IA em rápida evolução; custo/qualidade incertos
- *Decisão:* `AIProvider` como Protocol estrutural; factory `get_ai_provider()` como único ponto de troca
- *Reversão:* Implementar nova classe provider + atualizar `AI_PROVIDER` no `.env`

**ADR-003 — Fitness Functions no CI**
- *Contexto:* Características arquiteturais degradam silenciosamente sem validação automatizada
- *Decisão:* `pytest fitness/` falha o build se acoplamento, performance ou segurança regredirem
- *Consequência:* Dívida técnica arquitetural se torna visível imediatamente

---

## Como Executar

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar a aplicação
uvicorn main:app --reload

# Documentação interativa
open http://localhost:8000/docs
```

## Fitness Functions

```bash
# Todas as fitness functions
pytest fitness/ -v

# Por característica
pytest fitness/test_coupling.py -v      # acoplamento entre camadas
pytest fitness/test_performance.py -v  # SLOs de resposta
pytest fitness/test_security.py -v     # validação de segurança
pytest fitness/test_modularity.py -v   # coesão e responsabilidade única
```

## Variáveis de Ambiente

```env
# .env
DATABASE_URL=sqlite+aiosqlite:///./nutriai.db
AI_PROVIDER=mock          # mock | openai
AI_API_KEY=               # necessário se AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
DEBUG=true
MAX_RESPONSE_TIME_MS=500
```

## Estrutura

```
├── main.py                          # Entry point — lifespan, rotas, middleware
├── pytest.ini                       # asyncio_mode=auto, testpaths=fitness
├── requirements.txt
├── src/
│   ├── config.py                    # Fonte única de verdade para configuração (ADR-001,002)
│   ├── models/                      # Entidades de domínio — camada mais interna
│   │   ├── base.py                  # DeclarativeBase compartilhado
│   │   ├── user.py                  # Usuário com dados antropométricos
│   │   ├── exam.py                  # Painel e resultados de exames
│   │   └── nutrition.py             # Plano nutricional gerado por IA
│   ├── repositories/                # Acesso a dados — Repository Pattern
│   │   ├── base.py                  # CRUD genérico e tipado
│   │   ├── user_repository.py
│   │   ├── exam_repository.py
│   │   └── nutrition_repository.py
│   ├── services/                    # Lógica de negócio + orquestração de IA
│   │   ├── ai_service.py            # Protocol + providers (ADR-002)
│   │   ├── exam_service.py
│   │   └── nutrition_service.py
│   ├── api/                         # Camada HTTP
│   │   ├── middleware.py            # ResponseTimeMiddleware (expõe X-Response-Time-Ms)
│   │   ├── dependencies.py          # Wiring de DI (único ponto de alto acoplamento aceito)
│   │   └── routes/                  # Endpoints por domínio
│   └── infrastructure/
│       └── database.py              # Engine, session factory, create_tables
└── fitness/                         # Fitness functions (ADR-003)
    ├── conftest.py                  # Fixtures: test_db, client (SQLite in-memory)
    ├── test_coupling.py             # Valida direção de dependências entre camadas
    ├── test_performance.py          # Valida SLOs de tempo de resposta
    ├── test_security.py             # Valida rejeição de inputs maliciosos
    └── test_modularity.py           # Valida coesão, tamanho e configuração