# NutriAI — App de Nutrição Personalizada com IA

Sistema de recomendação nutricional personalizada baseado em exames laboratoriais,
construído com **FastAPI** seguindo estritamente a **Arquitetura Hexagonal** de Alistair Cockburn.

---

## Arquitetura Hexagonal (Ports & Adapters)

```
                        ┌─────────────────────────────────────────┐
                        │              HEXÁGONO                   │
  ┌─────────────┐       │  ┌──────────┐       ┌──────────────┐   │       ┌─────────────────┐
  │  HTTP/REST  │──────▶│  │  Ports   │──────▶│   Domain     │   │──────▶│  PostgreSQL /   │
  │  (FastAPI)  │       │  │  Input   │       │  Entities    │   │       │  SQLite (ORM)   │
  └─────────────┘       │  │  (ABCs)  │       │  Services    │   │       └─────────────────┘
                        │  └──────────┘       │  Exceptions  │   │
  ┌─────────────┐       │                     └──────────────┘   │       ┌─────────────────┐
  │   CLI /     │──────▶│  ┌──────────┐                          │──────▶│  Claude AI API  │
  │  Outros     │       │  │  Ports   │   Application Services   │       │  (Anthropic)    │
  └─────────────┘       │  │  Output  │   (Use Case Impls)       │       └─────────────────┘
                        │  │  (ABCs)  │                          │
                        │  └──────────┘                          │       ┌─────────────────┐
                        └─────────────────────────────────────────┘──────▶│  SMTP / Email   │
                                                                          └─────────────────┘

        Adapters Primários          DENTRO DO HEXÁGONO          Adapters Secundários
        (Driving Adapters)                                       (Driven Adapters)
```

### Princípios aplicados

#### 1. Separação Inside / Outside

O **hexágono interno** contém:
- `domain/` — entidades, value objects, serviços de domínio, exceções
- `ports/` — interfaces abstratas (ABCs) que definem os contratos
- `application/` — implementações dos casos de uso (orquestração)

O **mundo externo** contém:
- `adapters/input/` — HTTP (FastAPI), CLI, filas, etc.
- `adapters/output/` — banco de dados, IA, email, etc.

**Regra inviolável:** o interior nunca importa do exterior. A direção das dependências aponta sempre para dentro.

#### 2. Ports são contratos, não implementações

Cada port é uma `ABC` Python pura. O domínio define **o que precisa**, não **como é feito**.

```python
# ports/output/ai_analysis_provider_port.py
class AIAnalysisProviderPort(ABC):
    @abstractmethod
    async def analyze(self, patient, exam, domain_findings) -> str: ...
```

A IA é tratada **exatamente como o banco de dados**: um sistema externo acessado via porta.
Trocar de Claude para GPT-4 é implementar esse ABC sem tocar em nada mais.

#### 3. Domain tem zero dependências externas

As entidades usam apenas `dataclasses` e `uuid` da stdlib Python.
O `NutritionAnalysisService` classifica exames laboratoriais com regras de negócio puras —
sem SQL, sem HTTP, sem IA. Isso garante testabilidade total com mocks zero.

```python
# Testável 100% sem infraestrutura
service = NutritionAnalysisService()
recommendations, findings = service.analyze_exam(exam, patient)
```

#### 4. Tratamento simétrico de todos os sistemas externos

O banco de dados, a IA (Claude), e o serviço de email são todos tratados da mesma forma:
- Cada um tem seu **port** (interface em `ports/output/`)
- Cada um tem seu **adapter** (implementação em `adapters/output/`)
- Nenhum deles é especial — todos são permutáveis

#### 5. Composition Root centralizado

`config/dependencies.py` é o único módulo que conhece **todas** as camadas simultaneamente.
É ali que adaptadores são instanciados e injetados nos casos de uso via FastAPI `Depends()`.
Os roteadores HTTP conhecem apenas as interfaces dos ports, nunca as implementações.

#### 6. Adapters traduzem formatos

Cada adapter é responsável pela tradução entre o formato do mundo externo e as entidades de domínio:

- **HTTP Adapter:** Pydantic Schema ↔ Command/Entity
- **Persistence Adapter:** SQLAlchemy Model ↔ Domain Entity (JSON para listas/nested)
- **AI Adapter:** string prompt ↔ Domain Entity → string response

---

## Fluxo de uma requisição

```
POST /api/v1/nutrition-plans/generate
    │
    ▼
[FastAPI Router] — converte JSON → GenerateNutritionPlanCommand
    │
    ▼
[GenerateNutritionPlanUseCaseImpl] — orquestra (application layer)
    │
    ├─▶ [PatientRepositoryPort] → SQLAlchemyPatientRepository → DB
    ├─▶ [LabExamRepositoryPort] → SQLAlchemyLabExamRepository → DB
    ├─▶ [NutritionAnalysisService] → lógica pura de domínio (sem I/O)
    ├─▶ [AIAnalysisProviderPort] → ClaudeAnalysisProvider → Anthropic API
    ├─▶ [NutritionPlanRepositoryPort] → SQLAlchemyNutritionPlanRepository → DB
    └─▶ [NotificationServicePort] → SMTPNotificationService → Email
    │
    ▼
[FastAPI Router] — converte Entity → NutritionPlanResponse JSON
```

---

## Configuração e execução

### 1. Pré-requisitos

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Variáveis de ambiente

```bash
cp .env.example .env
# Edite .env e configure ANTHROPIC_API_KEY
```

### 3. Iniciar o servidor

```bash
uvicorn main:app --reload
```

### 4. Documentação interativa

Acesse `http://localhost:8000/docs` (Swagger UI) ou `http://localhost:8000/redoc`.

---

## Endpoints principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/patients/` | Cadastrar paciente |
| `POST` | `/api/v1/lab-exams/` | Submeter exames laboratoriais |
| `POST` | `/api/v1/nutrition-plans/generate` | Gerar plano nutricional com IA |
| `GET`  | `/api/v1/nutrition-plans/{id}` | Buscar plano por ID |
| `GET`  | `/api/v1/nutrition-plans/patient/{patient_id}` | Histórico de planos do paciente |

### Tipos de exames suportados

`vitamin_d`, `ferritin`, `hemoglobin`, `vitamin_b12`, `folic_acid`, `fasting_glucose`,
`hba1c`, `ldl_cholesterol`, `hdl_cholesterol`, `triglycerides`, `tsh`, `zinc`,
`magnesium`, `calcium`, `uric_acid`

---

## Como trocar uma implementação

Para substituir o Claude por outro provedor de IA:

```python
# Crie um novo adapter
class OpenAIAnalysisProvider(AIAnalysisProviderPort):
    async def analyze(self, patient, exam, domain_findings) -> str:
        # Implementação com OpenAI
        ...

# Em config/dependencies.py, troque apenas esta linha:
def get_ai_provider(...) -> AIAnalysisProviderPort:
    return OpenAIAnalysisProvider(api_key=settings.openai_api_key)
```

Zero mudanças no domínio, nos casos de uso, ou em qualquer outro adapter.
Esse é o poder dos Ports & Adapters.

---

## Estrutura de diretórios

```
.
├── domain/                  # Hexágono interno — zero dependências externas
│   ├── entities/            # Entidades de negócio (Patient, LabExam, NutritionPlan)
│   ├── value_objects/       # Objetos de valor imutáveis (NutrientLevel, ExamValue)
│   ├── services/            # Serviços de domínio puros (NutritionAnalysisService)
│   └── exceptions.py        # Exceções de domínio tipadas
├── ports/                   # Contratos abstratos (ABCs)
│   ├── input/               # Ports primários — casos de uso
│   └── output/              # Ports secundários — repositórios e serviços externos
├── adapters/                # Implementações concretas
│   ├── input/http/          # Adapter HTTP: roteadores FastAPI + schemas Pydantic
│   └── output/
│       ├── persistence/     # Adapter BD: SQLAlchemy models + repositórios
│       ├── ai/              # Adapter IA: Claude (Anthropic API)
│       └── notification/    # Adapter email: SMTP assíncrono
├── application/             # Implementações dos casos de uso (dentro do hexágono)
├── config/                  # Configuração, banco de dados, composition root (DI)
├── main.py                  # Entry point — FastAPI app + lifespan
├── requirements.txt
└── .env.example