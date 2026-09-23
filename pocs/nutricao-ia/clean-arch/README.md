# Nutrition AI — Clean Architecture

App de nutrição personalizada com IA, baseado em exames laboratoriais do paciente.

---

## Estrutura de camadas

```
┌──────────────────────────────────────────────────────────┐
│                  Frameworks & Drivers                    │
│   frameworks/api  ·  frameworks/db  ·  frameworks/ai    │
│   FastAPI · SQLAlchemy · Anthropic SDK · Pydantic        │
├──────────────────────────────────────────────────────────┤
│                  Interface Adapters                      │
│              adapters/controllers/                       │
│   PatientController · ExamController · NutritionController│
├──────────────────────────────────────────────────────────┤
│                     Use Cases                            │
│   RegisterPatient · SubmitExamResults                    │
│   GenerateNutritionPlan · GetPatientReport               │
│   use_cases/ports/  ← contratos (ABC)                   │
├──────────────────────────────────────────────────────────┤
│                      Entities                            │
│   Patient · Exam · ExamMarker · NutritionPlan · Nutrient │
│   (Python puro — zero dependências externas)             │
└──────────────────────────────────────────────────────────┘
            ↑  dependências sempre apontam para dentro  ↑
```

---

## Decisões arquiteturais

### 1. Entities — regras de negócio puras

`entities/` contém apenas `dataclasses` da stdlib Python. Nenhuma importação de
FastAPI, SQLAlchemy ou Pydantic. As regras críticas de negócio vivem aqui:

- `ExamMarker.status` — classifica o marcador em normal/baixo/alto/crítico sem
  precisar de banco ou API.
- `Patient.bmi` e `bmi_classification` — cálculo de IMC é uma regra de domínio,
  não um helper de apresentação.
- `NutritionPlan.is_calorie_balanced` — validação de negócio que independe de
  como o plano foi gerado.

### 2. Ports em `use_cases/ports/` — não em `adapters/`

Os ports (interfaces `ABC`) pertencem ao núcleo porque é o núcleo que define o
contrato que o mundo externo deve respeitar, e não o contrário. Isso materializa
o **Dependency Inversion Principle**: o Use Case depende de uma abstração que ele
mesmo declara; o SQLAlchemy e o Anthropic dependem dessa mesma abstração para
implementá-la.

```
use_cases/generate_nutrition_plan.py
    └── depende de: AiNutritionServicePort (abstrato, mesmo pacote)

frameworks/ai/anthropic_service.py
    └── implementa: AiNutritionServicePort
    └── conhece: anthropic SDK
```

### 3. Pydantic apenas em `frameworks/api/schemas/`

Pydantic é uma ferramenta de validação de entradas HTTP — um detalhe de
infraestrutura. As Entities usam `dataclasses` + método `validate()` manual para
manter a independência. Isso permite reusar as Entities em CLIs, workers, testes
unitários sem nenhuma camada HTTP.

### 4. Controllers como Controller + Presenter unificados

Em Uncle Bob a responsabilidade de formatar a saída cabe ao **Presenter**. Neste
projeto, os controllers de REST executam essa conversão via métodos `_present_*()`
privados. A simplificação é intencional: em uma REST API, o "View Model" é o
próprio dict/JSON. Para uma UI com múltiplos canais de saída (HTML, PDF, gRPC),
o Presenter deve ser extraído para `adapters/presenters/`.

### 5. `frameworks/container.py` — injeção de dependência explícita

O container é o único lugar que conhece as implementações concretas. Ele usa
`fastapi.Depends` para compor o grafo de dependências em tempo de request:

```
FastAPI route → Controller ← Use Case ← Repository (concreto, injetado)
                                      ← AI Service  (concreto, injetado)
```

O Use Case nunca instancia seus próprios repositórios — ele recebe abstrações.

### 6. JSON columns para markers/meals (decisão de MVP)

Os marcadores de exame, refeições e nutrientes são armazenados como JSON nas
tabelas SQLite. Isso reduz o número de tabelas e migrações no MVP. Em produção,
substituir por tabelas relacionais (`exam_markers`, `meals`, `plan_nutrients`)
sem alterar nenhuma Entity ou Use Case — apenas os repositórios em
`frameworks/db/repositories/`.

---

## Fluxo principal: gerar plano nutricional

```
POST /patients/{id}/nutrition-plans
  │
  ├── frameworks/api/routes/nutrition_routes.py
  │     valida body (Pydantic), chama controller via Depends
  │
  ├── adapters/controllers/nutrition_controller.py
  │     monta GenerateNutritionPlanInput, chama use case
  │
  ├── use_cases/generate_nutrition_plan.py
  │     1. busca Patient (PatientRepositoryPort)
  │     2. busca Exam   (ExamRepositoryPort)
  │     3. valida que exam.patient_id == patient.id
  │     4. chama ai_service.generate_plan(patient, exam)
  │     5. plan.validate()
  │     6. salva (NutritionPlanRepositoryPort)
  │
  └── frameworks/ai/anthropic_service.py
        monta prompt com marcadores alterados → Claude → JSON → NutritionPlan entity
```

---

## Endpoints

| Método | Rota                                     | Descrição                     |
|--------|------------------------------------------|-------------------------------|
| POST   | `/patients/`                             | Cadastrar paciente            |
| GET    | `/patients/{id}/report`                  | Relatório completo do paciente|
| POST   | `/patients/{id}/exams/`                  | Submeter exame laboratorial   |
| POST   | `/patients/{id}/nutrition-plans/`        | Gerar plano nutricional com IA|
| GET    | `/health`                                | Health check                  |

Documentação interativa disponível em `/docs` (Swagger UI).

---

## Como executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env e preencher ANTHROPIC_API_KEY

# 3. Executar
uvicorn main:app --reload
```

---

## Como testar cada camada isoladamente

```python
# Entities — sem mock, sem framework
patient = Patient(id="1", name="Ana", ...)
assert patient.bmi_classification == "Peso normal"

# Use Cases — mock dos ports
repo = Mock(spec=PatientRepositoryPort)
repo.find_by_email.return_value = None
uc = RegisterPatient(patient_repository=repo)
output = uc.execute(RegisterPatientInput(...))

# AI Service — mock do port, sem chamar Anthropic
ai_mock = Mock(spec=AiNutritionServicePort)
ai_mock.generate_plan.return_value = NutritionPlan(...)
```

A independência de frameworks torna cada camada testável sem subir banco ou API.