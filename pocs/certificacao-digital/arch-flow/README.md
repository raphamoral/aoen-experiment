# Plataforma de Certificação Digital de Cursos Livres

API para emissão e verificação pública de certificados digitais de cursos livres,
construída com FastAPI seguindo os princípios de **Architecture for Flow** (Susanne Kaiser).

---

## Como executar

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# Acesse: http://localhost:8000/docs
```

---

## Architecture for Flow — Decisões

### 1. Wardley Mapping — Maturidade dos Componentes

Cada bounded context foi posicionado no mapa de Wardley para orientar
onde investir em inovação vs. onde usar soluções de prateleira.

| Componente | Maturidade | Justificativa |
|---|---|---|
| Verificação Pública | **Custom** | Interface de confiança — ainda sem padrão de mercado no Brasil |
| Emissão de Certificado | **Custom → Genesis** | Evolução planejada para W3C Verifiable Credentials |
| Motor de Avaliação | **Custom** | Lógica de pesos e tentativas é diferencial competitivo |
| Catálogo de Cursos | **Product** | Funcionalidade bem conhecida; equivalente a Udemy/Hotmart |
| Gestão de Matrículas | **Product** | Padrão de mercado; foco em integração, não inovação |
| Barramento de Eventos | **Custom → Commodity** | In-memory (MVP); migrar para Kafka/RabbitMQ ao escalar |
| Autenticação JWT | **Commodity** | Solução de prateleira; zero diferencial competitivo |
| Banco de Dados SQLite | **Commodity** | Trocar `DATABASE_URL` por PostgreSQL sem mudar nada mais |

**Implicação prática**: times dedicados ao que é Custom/Genesis; soluções SaaS
para o que é Product/Commodity.

---

### 2. Team Topologies — Organização por Fluxo de Valor

```
┌─────────────────────────────────────────────────────────────┐
│  Stream-aligned Team A: "Jornada de Aprendizado"            │
│  contexts/course_catalog/ + contexts/enrollment/            │
│  Missão: o estudante encontra, se matricula e avança        │
└──────────────────────────┬──────────────────────────────────┘
                           │ evento: MatriculaConcluida
┌──────────────────────────▼──────────────────────────────────┐
│  Stream-aligned Team B: "Certificação e Confiança"          │
│  contexts/assessment/ + contexts/certification/             │
│  + contexts/verification/                                   │
│  Missão: a credencial é emitida, válida e verificável       │
└──────────────────────────┬──────────────────────────────────┘
                           │ usa como serviço
┌──────────────────────────▼──────────────────────────────────┐
│  Platform Team: "Infraestrutura Compartilhada"              │
│  shared/kernel/ (database, event_bus, auth)                 │
│  Missão: reduzir carga cognitiva dos times stream-aligned   │
└─────────────────────────────────────────────────────────────┘
```

O contexto `verification/` é **propositalmente separado** de `certification/`:
permite que a API pública (sem autenticação, alta disponibilidade, cacheable)
evolua em ritmo diferente do domínio interno de emissão.

---

### 3. Bounded Contexts e Linguagem Ubíqua

Cada contexto tem seu próprio vocabulário. O mesmo conceito tem nomes
diferentes entre contextos — e isso é correto (não unificar forçosamente).

| Contexto | Agregado Raiz | Termos Chave |
|---|---|---|
| **Catálogo de Cursos** | `Curso` | Publicar, Arquivar, Maturidade, Módulo, Aula |
| **Matrícula** | `Matricula` | Matricular, Concluir Aula, Progresso, Percentual de Conclusão |
| **Avaliação** | `Avaliacao` | Questão, Alternativa, Tentativa, Submeter, Reprovar, Aprovar |
| **Certificação** | `Certificado` | Emitir, Revogar, Hash de Verificação, Credencial |
| **Verificação** | `ResultadoVerificacao` | Verificar, Autenticidade, Auditoria |

**Nota sobre "Estudante"**: intencionalmente ausente como entidade própria neste MVP.
O estudante é representado apenas pelo `estudante_id` (referência externa).
Em produção: adicionar `contexts/identity/` como contexto separado.

---

### 4. Fluxo de Valor (Value Stream)

```
Instrutor cadastra Curso
        ↓
Curso é Publicado (invariante: precisa ter módulos)
        ↓
Estudante se Matricula
        ↓
Estudante Conclui Aulas → evento: MatriculaConcluidaEvento
        ↓
Estudante Submete Tentativa na Avaliação
        ↓
[Aprovado] → evento: AvaliacaoAprovadaEvento
        ↓
Certificado é Emitido → evento: CertificadoEmitidoEvento
        ↓
Qualquer pessoa Verifica via hash público (sem autenticação)
```

O fluxo é orientado a eventos: cada contexto reage a eventos dos anteriores
sem acoplamento direto (Anticorruption Layer via `event_handlers.py`).

---

### 5. Anticorruption Layer (ACL)

`contexts/certification/application/event_handlers.py` é o ACL principal:

- Recebe `AvaliacaoAprovadaEvento` (vocabulário de Avaliação)
- Traduz para `EmitirCertificadoRequest` (vocabulário de Certificação)
- O contexto Certificação **nunca importa** modelos de Avaliação diretamente

Isso preserva a autonomia de evolução de cada contexto.

---

### 6. Estrutura de Diretórios

```
contexts/
  course_catalog/      # Catálogo de Cursos — maturidade: Product
  enrollment/          # Matrícula — maturidade: Product
  assessment/          # Avaliação — maturidade: Custom
  certification/       # Certificação — maturidade: Custom→Genesis
  verification/        # Verificação Pública — maturidade: Custom

shared/
  kernel/
    domain/            # Entity, ValueObjects, DomainEvents (Shared Kernel)
    infrastructure/    # Database, EventBus (Platform Team)
    auth/              # JWT (Commodity)
```

Cada contexto segue a mesma estrutura interna:
```
<contexto>/
  domain/         # Modelos, repositórios abstratos (puro Python, sem frameworks)
  application/    # Use cases, DTOs (orquestra domínio; não conhece HTTP)
  infrastructure/ # ORM, implementações concretas (SQLAlchemy)
  api/            # Routers FastAPI (traduz HTTP para use cases)
```

---

### 7. Plano de Evolução (Wardley → Decisões Técnicas)

| Hoje (MVP) | Próximo passo | Quando migrar |
|---|---|---|
| SQLite | PostgreSQL | Antes de produção |
| Event bus in-memory | RabbitMQ/Kafka | Ao separar em microserviços |
| Hash SHA-256 simples | W3C Verifiable Credentials | Ao exigir portabilidade internacional |
| JWT local | OAuth2/OIDC (Keycloak) | Ao integrar com sistemas externos |
| Monolito modular | Microserviços por contexto | Quando times crescerem e precisarem de deploys independentes |

A arquitetura atual é um **monolito modular** — os contextos compartilham
banco de dados mas têm fronteiras claras de código. A migração para
microserviços é uma decisão de deployment, não de reescrita.