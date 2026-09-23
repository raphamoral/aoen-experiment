# NutriAI — Nutrição Personalizada por Exames Laboratoriais

Plataforma de recomendações nutricionais baseadas em análise clínica de biomarcadores com IA.

## Arquitetura AOEN

### Fase 1 — NÚCLEO (VALOR)

**Core diferenciador:** análise de biomarcadores laboratoriais com regras clínicas baseadas em evidências + narrativa personalizada gerada por IA.

**Implementação:**
- `core/analyzer.py` — análise pura: severidade, scores de risco, flags clínicos (HOMA-IR, anemia, disfunção tireoidiana). **Zero dependências externas.**
- `core/nutrition_engine.py` — mapeamento biomarcador → recomendação nutricional estruturada. **Zero dependências externas.**

**Por que assim:** o núcleo é testável de forma completamente isolada (`pytest core/`), benchmarkável por chamada e extraível para microserviço sem tocar na camada de API. A Service Layer conhece o core; o core não conhece nada além de Python puro.

---

### Fase 2 — MULTI-INTERFACE (ALCANCE)

A mesma Service Layer serve múltiplas interfaces sem código duplicado:

| Interface | Mercado |
|---|---|
| REST API → app mobile | Pacientes monitorando saúde |
| REST API → dashboard web | Nutricionistas e clínicas |
| REST API → integração B2B | Hospitais e planos de saúde |
| REST API → wellness app | Fitness e bem-estar |

**Implementação:** `routers/` são deliberadamente finos — apenas validam input, chamam o service e serializam a resposta. Toda lógica vive em `services/`, pronta para ser chamada por qualquer interface futura (CLI, job assíncrono, webhook).

---

### Fase 3 — CONFIG-DRIVEN (ESCALA)

O fluxo é fixo no código: `exame → análise → plano → recomendações`. Os parâmetros são configuráveis por tenant sem deploy:

```python
# config.py — nenhuma linha de código muda entre tenants
TENANT_CONFIGS = {
    "hospital_basic":  TenantConfig(ai_model="claude-haiku-4-5-20251001", max_daily_analyses=2000, include_supplements=False),
    "clinic_premium":  TenantConfig(ai_model="claude-opus-4-6",           max_daily_analyses=500,  include_supplements=True),
    "wellness_app":    TenantConfig(ai_model="claude-sonnet-4-6",          report_language="en-US"),
}
```

**Parâmetros configuráveis por tenant:**
- Modelo de IA (haiku → custo baixo para volume; opus → qualidade máxima para premium)
- Biomarcadores habilitados
- Faixas de referência customizadas por laboratório
- Idioma do relatório
- Inclusão de recomendações de suplementos e estilo de vida
- Limite de análises diárias

---

### Fase 4 — ISOLAMENTO (CUSTO)

**Core isolado = custo mensurável:**

```
Tenant hospital_basic:  1 análise = 1 chamada core/analyzer.analyze()  (zero custo de IA)
Tenant clinic_premium:  1 plano   = 1 chamada core/ + 1 chamada Claude Opus (custo rastreável)
Tenant wellness_app:    1 plano   = 1 chamada core/ + 1 chamada Claude Sonnet
```

**Implementação:**
- `core/` tem zero imports externos — pode rodar em processo separado (Celery worker, Lambda)
- `ExamAnalysis` persiste o resultado da análise — custo do core pago uma única vez por exame
- `AIService` é o único ponto de contato com a API externa — fácil de instrumentar e limitar por tenant

**Próximo passo natural:** extrair `core/` para um worker assíncrono (Celery + Redis) sem refatorar nada além de `services/exam_service.py`.

---

## Estrutura

```
nutriai/
├── main.py                     # FastAPI app, middlewares, lifespan
├── database.py                 # Async SQLAlchemy engine + sessão
├── models.py                   # Patient, LabExam, ExamAnalysis, NutritionPlan
├── config.py                   # TenantConfig + faixas de referência
├── core/
│   ├── analyzer.py             # NÚCLEO: análise de biomarcadores (sem deps)
│   └── nutrition_engine.py     # NÚCLEO: engine de recomendações (sem deps)
├── services/
│   ├── exam_service.py         # Orquestração de exames
│   ├── nutrition_service.py    # Orquestração de planos nutricionais
│   └── ai_service.py           # Wrapper Anthropic SDK
└── routers/
    ├── patients.py             # CRUD de pacientes
    ├── exams.py                # Submissão e análise de exames
    └── nutrition.py            # Geração e consulta de planos
```

---

## Setup

```bash
pip install -r requirements.txt

# Criar .env com:
# ANTHROPIC_API_KEY=sk-ant-...
# DATABASE_URL=sqlite+aiosqlite:///./nutriai.db   (ou PostgreSQL)

uvicorn main:app --reload
# Docs: http://localhost:8000/docs
```

---

## Fluxo Principal da API

```
# 1. Identificar tenant via header
X-Tenant-ID: clinic_premium

# 2. Cadastrar paciente
POST /api/v1/patients/
{"name": "Maria Silva", "email": "maria@email.com", "birth_date": "1985-03-15", "sex": "F"}

# 3. Submeter exame com biomarcadores
POST /api/v1/exams/
{"patient_id": "...", "exam_date": "2026-04-01", "biomarkers": {"vitamin_d": 18.5, "ferritin": 8.2, "tsh": 5.8}}

# 4. Analisar exame (aciona core/ isolado)
POST /api/v1/exams/{exam_id}/analyze
→ overall_score: 41.2, flags: ["SEVERE_VITAMIN_D_DEFICIENCY", "HYPOTHYROIDISM_SUSPECTED"]

# 5. Gerar plano nutricional com IA
POST /api/v1/nutrition/generate
{"patient_id": "...", "analysis_id": "..."}

# 6. Consultar plano completo com recomendações
GET /api/v1/nutrition/{plan_id}
→ ai_narrative + recommendations ordenadas por prioridade clínica
```

---

## Decisões de Design

| Decisão | Motivo AOEN |
|---|---|
| `core/` sem imports externos | Isolamento — testável, benchmarkável, extraível |
| Biomarcadores como JSON no modelo | Schema flexível por tenant sem migrações |
| `X-Tenant-ID` via header HTTP | Multi-tenant sem subdomínio; roteamento não muda |
| Modelo de IA configurável por tenant | Custo mensurável; tenant premium paga por Claude Opus |
| `ExamAnalysis` persiste resultado do core | Idempotência; custo de análise pago uma vez |
| Service Layer separada dos routers | Mesma lógica serve REST, CLI, workers futuros |
| `AIService` isolado de `core/` | Core testável sem API key; custo de IA rastreável separadamente |