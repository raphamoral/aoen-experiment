# Marketplace de Freelancers em Compliance Regulatório

API REST construída com **FastAPI** seguindo estritamente a
**Arquitetura Hexagonal** de Alistair Cockburn (Ports & Adapters).

---

## Estrutura do Projeto

```
.
├── domain/                         # INSIDE — zero dependências externas
│   ├── entities/                   # Objetos de negócio com identidade
│   │   ├── freelancer.py
│   │   ├── client.py
│   │   ├── project.py
│   │   ├── proposal.py
│   │   └── contract.py
│   ├── value_objects/              # Imutáveis, sem identidade própria
│   │   ├── compliance_area.py      # Enum: LGPD, GDPR, SOX, Basel III…
│   │   ├── expertise_level.py
│   │   └── rate.py                 # HourlyRate com validação de moeda
│   ├── services/                   # Lógica de domínio pura (stateless)
│   │   ├── matching_service.py     # Elegibilidade e ranking de candidatos
│   │   └── proposal_service.py     # Rejeição de propostas concorrentes
│   └── exceptions.py               # Erros semânticos do domínio
│
├── ports/                          # FRONTEIRA — contratos abstratos (ABCs)
│   ├── inbound/                    # O que o mundo externo pode pedir ao domínio
│   │   ├── freelancer_use_case.py  # IFreelancerUseCase
│   │   ├── project_use_case.py     # IProjectUseCase
│   │   └── proposal_use_case.py    # IProposalUseCase
│   └── outbound/                   # O que o domínio precisa do mundo externo
│       ├── freelancer_repository.py
│       ├── project_repository.py
│       ├── proposal_repository.py
│       ├── notification_service.py  # INotificationService
│       └── payment_service.py       # IPaymentService
│
├── application/                    # INSIDE — orquestra domínio + portas de saída
│   ├── freelancer_service.py       # Implementa IFreelancerUseCase
│   ├── project_service.py          # Implementa IProjectUseCase
│   └── proposal_service.py         # Implementa IProposalUseCase
│
├── adapters/                       # OUTSIDE — implementações concretas
│   ├── inbound/                    # Adaptadores que dirigem o domínio
│   │   ├── http/                   # FastAPI (poderia ser CLI, gRPC, etc.)
│   │   │   ├── freelancer_router.py
│   │   │   ├── project_router.py
│   │   │   └── proposal_router.py
│   │   └── schemas/                # Pydantic — traduz HTTP ↔ domínio
│   └── outbound/                   # Adaptadores dirigidos pelo domínio
│       ├── persistence/            # In-memory (troque por SQLAlchemy)
│       ├── notification/           # SMTP stub (troque por fastapi-mail)
│       └── payment/                # Stripe stub (troque por stripe-python)
│
├── container.py                    # Composition Root — única cola entre camadas
└── main.py                         # Bootstrap FastAPI
```

---

## Decisões de Arquitetura Hexagonal

### 1. Separação Inside / Outside

| Camada | Módulos | Dependências permitidas |
|--------|---------|------------------------|
| Inside | `domain/`, `application/` | Apenas entre si |
| Fronteira | `ports/` | Apenas `domain/` |
| Outside | `adapters/` | `ports/` e `domain/` |

**O `domain/` nunca importa nada de `adapters/`.** Isso garante que a lógica de negócio é testável sem infraestrutura.

### 2. Ports são Interfaces Abstratas

Cada porta é uma `ABC` (Abstract Base Class) Python:

- **Portas de entrada** (`ports/inbound/`): definem os *casos de uso* que os adaptadores externos podem invocar. Ex.: `IFreelancerUseCase.register_freelancer(...)`.
- **Portas de saída** (`ports/outbound/`): definem o que o domínio *precisa* de sistemas externos. Ex.: `INotificationService.notify_proposal_accepted(...)`.

Os serviços de aplicação dependem apenas das ABCs — nunca das implementações concretas.

### 3. Adapters Conectam ao Mundo Externo

Cada adaptador implementa exatamente uma porta:

| Adaptador | Porta implementada | Sistema externo |
|-----------|-------------------|-----------------|
| `SMTPNotificationService` | `INotificationService` | Servidor SMTP |
| `StripePaymentService` | `IPaymentService` | Stripe API |
| `InMemoryFreelancerRepository` | `IFreelancerRepository` | Memória (dev) |
| `freelancer_router` (FastAPI) | chama `IFreelancerUseCase` | HTTP/REST |

Para trocar SMTP por WhatsApp, basta criar `WhatsAppNotificationService(INotificationService)` e alterar `container.py`.

### 4. Tratamento Simétrico de Sistemas Externos

HTTP (entrada) e SMTP/Stripe (saída) são tratados da mesma forma: ambos ficam em `adapters/` e se comunicam com o domínio exclusivamente via portas. Não há tratamento especial para nenhum protocolo.

### 5. Composition Root

`container.py` é o único arquivo que conhece tanto as interfaces quanto as implementações. Ele usa `app.dependency_overrides` do FastAPI para injetar as dependências concretas nos routers, que tipam seus parâmetros apenas com as ABCs.

---

## Como Executar

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Acesse a documentação interativa em: `http://localhost:8000/docs`

---

## Fluxo Principal: Submissão e Aceitação de Proposta

```
Cliente HTTP
    │
    ▼
[Adapter Inbound] proposal_router.py
    │  chama porta de entrada
    ▼
[Port Inbound] IProposalUseCase
    │  implementada por
    ▼
[Application] ProposalApplicationService
    │  valida elegibilidade via domínio
    ├──► FreelancerMatchingService  (domínio puro)
    │  persiste via porta de saída
    ├──► IProposalRepository        (porta de saída)
    │  notifica via porta de saída
    └──► INotificationService       (porta de saída)
              │  implementada por
              ▼
         [Adapter Outbound] SMTPNotificationService
```

---

## Como Trocar de In-Memory para PostgreSQL

1. Implemente `SQLAlchemyFreelancerRepository(IFreelancerRepository)` em `adapters/outbound/persistence/`.
2. No `container.py`, substitua:
   ```python
   # antes
   _freelancer_repo = InMemoryFreelancerRepository()
   # depois
   _freelancer_repo = SQLAlchemyFreelancerRepository(session=db_session)
   ```
3. Nenhum outro arquivo precisa ser alterado.

---

## Áreas de Compliance Suportadas

`LGPD · GDPR · SOX · BASEL_III · AML_KYC · ISO_27001 · PCI_DSS · HIPAA · COBIT · COSO · IFRS · CVM`