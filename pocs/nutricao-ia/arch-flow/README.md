# NutriAI — Nutrição Personalizada com IA baseada em Exames Laboratoriais

Projeto estruturado segundo **Architecture for Flow** (Susanne Kaiser), combinando Domain-Driven Design, Wardley Mapping e Team Topologies para maximizar o fluxo de valor e minimizar a carga cognitiva dos times.

---

## Wardley Map — Posicionamento por Maturidade Evolutiva

```
Visibilidade
    ^
    |  [Insights IA Personalizados]        ← Genesis  (núcleo diferenciador)
    |  [Correlação Biomarcador-Nutriente]  ← Custom   (conhecimento proprietário)
    |  [Ingestão de Exames]               ← Custom   (pipeline de parsing)
    |  [Plano Nutricional]                ← Custom   (personalização por exame)
    |  [Perfil de Usuário]                ← Product  (funcionalidade madura)
    |  [Event Bus]                        ← Product  (Kafka/SQS em produção)
    |  [Banco de Dados]                   ← Commodity
    |  [Autenticação]                     ← Commodity
    +-------------------------------------------------> Evolução
       Genesis      Custom      Product    Commodity
```

**Decisão-chave**: O investimento de engenharia deve se concentrar no eixo Genesis/Custom — é onde está o diferencial competitivo. Perfil e infraestrutura devem usar soluções prontas (Product/Commodity).

---

## Bounded Contexts e Linguagem Ubíqua

### `contexts/laboratory` — Contexto Laboratorial
**Wardley**: Custom Build | **Team**: Stream-aligned

Responsabilidade: ingestão e estruturação de resultados de exames.

**Linguagem Ubíqua**:
| Termo | Significado no Domínio |
|---|---|
| `ResultadoLaboratorial` | O exame completo como unidade transacional |
| `Biomarcador` | Parâmetro bioquímico específico (Vitamina D, TSH, Ferro...) |
| `FaixaDeReferência` | Intervalo de valores clínicos normais |
| `ValorBiomarcador` | Medição numérica com unidade validada |

**Eventos publicados**:
- `LabResultReceived` → subscrito por `ai_analysis`
- `BiomarkerOutOfRange` → subscrito por `nutrition`, `ai_analysis`

---

### `contexts/ai_analysis` — Contexto de Análise por IA
**Wardley**: **Genesis** (core differentiator) | **Team**: Complicated Subsystem

Responsabilidade: geração de insights clínicos usando LLM (Claude/Anthropic).

**Linguagem Ubíqua**:
| Termo | Significado no Domínio |
|---|---|
| `AnálisePersonalizada` | Resultado do raciocínio clínico da IA |
| `InsightDeSaúde` | Correlação identificada com recomendação acionável |
| `NívelDeRisco` | Classificação de impacto: crítico/alto/moderado/baixo |

**Padrões aplicados**:
- **Anti-Corruption Layer**: `AnthropicLLMGateway` isola o domínio da API do LLM — o domínio recebe `HealthInsight`, não JSON bruto do modelo
- **Structured Output**: prompt engineering garante resposta JSON tipada

**Eventos publicados**:
- `AnalysisGenerated` → subscrito por `user_profile`
- `CriticalInsightFound` → aciona notificação prioritária

---

### `contexts/nutrition` — Contexto Nutricional
**Wardley**: Custom Build | **Team**: Stream-aligned (enabling)

Responsabilidade: tradução de biomarcadores em planos nutricionais terapêuticos.

**Linguagem Ubíqua**:
| Termo | Significado no Domínio |
|---|---|
| `PlanoNutricional` | Conjunto de recomendações derivadas do exame |
| `MetaDeIngestãoDiária` | Quantidade recomendada de nutriente por dia |
| `Deficiência` | Carência nutricional identificada pelos biomarcadores |
| `RestriçãoAlimentar` | Limitação clínica ou terapêutica do plano |

**Eventos publicados**:
- `NutritionalPlanCreated` → subscrito por `user_profile`
- `DeficiencyIdentified` → subscrito por `ai_analysis`

---

### `contexts/user_profile` — Contexto de Perfil
**Wardley**: Product | **Team**: Platform

Responsabilidade: capacidade de plataforma compartilhada entre todos os contexts.

O método `to_ai_context()` é a **camada de tradução** entre o perfil do usuário e o contrato esperado pelo `ai_analysis`, evitando acoplamento direto entre contexts.

---

## Shared Kernel — Mínimo e Intencional

```
shared/
├── kernel/
│   ├── entity.py          # Identidade por ID — igualdade por ID, não atributos
│   ├── value_object.py    # Imutável, sem identidade — igualdade por atributos
│   ├── aggregate_root.py  # Consistência transacional + coleta de eventos
│   └── domain_event.py    # Fato imutável do domínio
└── events/
    └── event_bus.py       # Integração assíncrona entre contexts (dev: in-memory)
```

**Regra**: nunca coloque regras de negócio no Shared Kernel. Apenas blocos de construção genéricos do DDD.

---

## Team Topologies Aplicado

```
┌──────────────────────────────────────────────────────────────┐
│                    Stream-Aligned Teams                       │
│   laboratory + nutrition  (fluxo principal de valor)         │
│   → Respondem a mudanças de negócio de forma independente    │
└──────────────────────────────────────────────────────────────┘
                              ↑ complicated subsystem
             ┌────────────────────────────────────┐
             │       Complicated Subsystem Team    │
             │       ai_analysis                  │
             │  Requer: IA + clínica + nutrição   │
             │  Não sobrecarregar stream-aligned  │
             └────────────────────────────────────┘
                              ↑ platform
┌──────────────────────────────────────────────────────────────┐
│                      Platform Team                            │
│   user_profile  (identidade, perfil, contexto clínico)       │
│   → API interna consumida pelos demais contexts              │
└──────────────────────────────────────────────────────────────┘
```

---

## Fluxo de Valor Principal

```
1. [user_profile]   Usuário cria perfil
                    → UserProfileCreated (evento)

2. [laboratory]     Exame laboratorial é carregado
                    → LabResultReceived (evento)
                    → BiomarkerOutOfRange (por biomarcador alterado)

3. [ai_analysis]    Claude analisa biomarcadores + contexto do usuário
                    → Correlações clínicas → HealthInsights estruturados
                    → AnalysisGenerated (evento)
                    → CriticalInsightFound (se risco crítico)

4. [nutrition]      Biomarcadores alterados → metas nutricionais terapêuticas
                    → NutritionalPlanCreated (evento)

5. [todos]          Novos exames refinam análises continuamente
```

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows

pip install -r requirements.txt

export ANTHROPIC_API_KEY="sua-chave-aqui"

uvicorn main:app --reload --port 8000
```

Documentação interativa: `http://localhost:8000/docs`

---

## Evolução Arquitetural

| Contexto | Próximo Passo | Direção Wardley |
|---|---|---|
| `ai_analysis` | Fine-tuning em nutrição clínica + RAG com estudos | Genesis → Custom |
| `laboratory` | Integração com APIs de laboratórios (OCR de PDFs) | Custom → Product |
| `event_bus` | Migrar para Apache Kafka (deploy independente por context) | Product → Commodity |
| `database` | PostgreSQL + read replicas + Redis para planos ativos | Commodity otimizado |