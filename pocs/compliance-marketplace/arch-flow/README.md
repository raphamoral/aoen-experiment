# ComplianceHub — Marketplace de Freelancers em Compliance Regulatório

Arquitetura baseada em **Architecture for Flow** de Susanne Kaiser:
**Domain-Driven Design + Wardley Mapping + Team Topologies**

---

## Por que Architecture for Flow?

Marketplaces de nicho falham quando tratam todos os componentes como igualmente
estratégicos. Architecture for Flow força a pergunta: **onde está a inovação, e o
que é infraestrutura?** A resposta molda a organização dos times, a escolha de
tecnologias e onde investir em diferenciação versus commoditização.

---

## Mapa Wardley — Decisões Arquiteturais

```
                    GENESIS → CUSTOM → PRODUCT → COMMODITY

Visibilidade
(valor para
o cliente)
    ▲
    │  Matching Algorithm ──────────────────────────────── [GENESIS]
    │  Compliance Catalog ──────────────────────────── [CUSTOM]
    │  Freelancer Profile ──────────────────────────── [CUSTOM]
    │  Contracting / E-sign ─────────────────────── [PRODUCT]
    │  Auth / Identity ─────────────────────────────────── [COMMODITY]
    │  Payment Processing ──────────────────────────────── [COMMODITY]
    │
    └─────────────────────────────────────────────────────────────────▶
                                                              Evolução
```

### Classificações e consequências

| Componente           | Maturidade  | Decisão                                               |
|----------------------|-------------|-------------------------------------------------------|
| Matching Algorithm   | **Genesis** | Desenvolver internamente. NÃO terceirizar. Vantagem competitiva central. |
| Compliance Catalog   | **Custom**  | Curar internamente. Monitorar players RegTech (Bloomberg Law, Lextree). |
| Freelancer Profile   | **Custom**  | Diferencial: validação editorial, jurisdições, certificações. |
| Contracting          | **Product** | Integrar ClickSign/DocuSign via Anti-Corruption Layer. |
| Identity             | **Commodity** | Delegar para Auth0/Keycloak. Zero código de auth. |
| Payment              | **Commodity** | Integrar Pagar.me/Stripe. Apenas Anti-Corruption Layer. |

---

## Bounded Contexts (Domain-Driven Design)

### Regras de isolamento

- Cada contexto tem seu próprio modelo de domínio — sem compartilhamento de entidades
- Comunicação entre contextos via **Domain Events** (event bus) ou **Anti-Corruption Layer**
- Linguagem ubíqua é local a cada contexto (um "User" em Identity ≠ "Freelancer" em Freelancer)

### Contexto: Identity (Commodity)

**Responsabilidade:** autenticação e autorização de usuários.

**Por que commodity?** Problemas de auth são resolvidos há décadas. Investir nisso
é desperdício de energia de times. Em produção, substituir completamente por Auth0
ou Keycloak — o código de Identity aqui existe apenas para o protótipo funcionar.

**Ubiquitous Language:** User, Email, UserRole (freelancer | client | admin), JWT

---

### Contexto: Freelancer Profile (Custom)

**Responsabilidade:** ciclo de vida do perfil de freelancers especializados.

**Por que custom?** O diferencial não é "ter perfis" — é ter perfis com
**validação editorial de expertise regulatória**, rastreamento de certificações
profissionais (CCEP, CISA, CFE) e mapeamento de jurisdições. Isso não existe
pronto em plataforma genérica de freelancers.

**Ubiquitous Language:**
- **Freelancer** = profissional autônomo especializado em compliance regulatório
- **Especialização** = domínio de expertise em framework regulatório específico (LGPD, BACEN...)
- **Certificação** = credencial profissional verificável externamente
- **Jurisdição** = âmbito geográfico e normativo de atuação regulatória
- **Aprovação** = validação editorial pela equipe de compliance da plataforma

**Domain Events emitidos:**
- `FreelancerRegistered` → notifica time editorial para revisão
- `FreelancerApproved` → torna perfil visível para matching
- `SpecializationAdded` → atualiza índice de matching

---

### Contexto: Compliance Catalog (Custom → Product)

**Responsabilidade:** repositório estruturado de frameworks regulatórios brasileiros
e internacionais (LGPD, BACEN 4.658, CVM 598, COAF AML, GDPR, SOX...).

**Por que custom?** Hoje é diferencial — a curadoria técnica e taxonomia proprietária
criam valor. No mapa Wardley, monitora-se a evolução para **Product**: players RegTech
como Bloomberg Law e Lextree estão commoditizando catálogos regulatórios. Planejar
extração para API externa quando viável.

**Ubiquitous Language:**
- **Framework** = conjunto normativo (lei, resolução, circular, norma técnica)
- **Órgão Regulador** = entidade emissora da norma (BACEN, CVM, SUSEP, ANPD, COAF)
- **Requisito** = obrigação específica dentro de um framework
- **Complexidade** = nível de especialização exigida (1=básico → 4=especialista)

---

### Contexto: Matching (Genesis)

**Responsabilidade:** algoritmo proprietário de correspondência entre
requisitos de projetos de compliance e perfis de freelancers.

**Por que genesis?** É a inovação central da plataforma. Não existe solução
de prateleira para matching especializado em expertise regulatória. O algoritmo
considera dimensões que plataformas genéricas ignoram:

**Score de Matching — Dimensões e Pesos:**

| Dimensão              | Peso | Justificativa                                          |
|-----------------------|------|--------------------------------------------------------|
| Framework Alignment   | 40%  | Domínio da norma específica é inegociável              |
| Jurisdiction Match    | 20%  | Normas nacionais têm especificidades locais críticas   |
| Seniority Fit         | 20%  | Complexidade regulatória exige experiência proporcional |
| Availability Fit      | 10%  | Restrição operacional                                  |
| Certification Bonus   | 10%  | Certificações como sinal de qualidade verificável      |

**Evolução prevista (Wardley):**
- Agora (Genesis): algoritmo determinístico baseado em regras
- 6 meses (Custom): modelo ML com dados históricos de contratos
- 12 meses (Product): API de recomendação com feedback loop

**Ubiquitous Language:**
- **Match** = proposta de conexão entre cliente e freelancer
- **Score** = índice de compatibilidade calculado pelo algoritmo [0.0–1.0]
- **Requisito** = necessidade regulatória declarada pelo cliente
- **Threshold** = score mínimo para o match ser apresentado (0.30)

---

### Contexto: Contracting (Product)

**Responsabilidade:** ciclo de vida do contrato entre cliente e freelancer.

**Por que product?** Assinatura digital é commodity (DocuSign, ClickSign existem).
O que é custom é a modelagem de **entregáveis de compliance** — especializados
no domínio regulatório. Integrar provider externo via Anti-Corruption Layer.

**Domain Events emitidos:**
- `ContractCreated` → notifica partes para revisar escopo
- `ContractSigned` → ativa execução do projeto
- `ContractCompleted` → dispara liberação de pagamento ao freelancer

**Ubiquitous Language:**
- **Contrato** = acordo formal com validade jurídica para projeto de compliance
- **Entregável** = produto concreto e mensurável (ex: "Mapeamento de Dados LGPD")
- **Vigência** = período de execução acordado entre as partes
- **Assinatura** = aceite digital com validade jurídica (MP 2.200-2/2001)

---

### Contexto: Payment (Commodity)

**Responsabilidade:** processamento de pagamentos e repasse ao freelancer.

**Por que commodity?** Pagamentos são completamente resolvidos por Pagar.me,
Stripe, PagSeguro. Zero lógica de negócio relevante aqui além do modelo de
taxa da plataforma (10% gross margin).

**Modelo financeiro:**
```
Valor bruto (cliente paga)     R$ 10.000
(-) Taxa plataforma (10%)      R$  1.000
(=) Repasse ao freelancer      R$  9.000
```

---

## Team Topologies

### Stream-aligned Teams (fluxo de valor direto)

- **Time Freelancer**: onboarding, aprovação editorial, enriquecimento de perfil
- **Time Cliente**: jornada de busca, requisitos de projeto, matching
- **Time Compliance**: curadoria do catálogo regulatório

### Platform Teams (habilitadores)

- **Time Plataforma**: Identity (Auth0), Payment (Pagar.me), infraestrutura
- **Time DevEx**: padrões de API, event bus, observabilidade

### Complicated Subsystem Team

- **Time Matching**: algoritmo proprietário de matching — expertise especializada
  em ML + compliance. Protegido de demandas de outros times.

### Interaction Modes

- Stream-aligned ↔ Platform: **X-as-a-Service** (consumo de APIs)
- Stream-aligned ↔ Complicated Subsystem: **X-as-a-Service** (API de matching)
- Stream-aligned ↔ Stream-aligned: **Collaboration** (curta duração, depois X-as-a-Service)

---

## Estrutura do Projeto

```
compliancehub/
├── shared/
│   ├── kernel/              # Building blocks DDD: Entity, ValueObject, AggregateRoot,
│   │                        # DomainEvent, Repository
│   ├── events/              # Event Bus — desacopla bounded contexts
│   └── infrastructure/      # Config, Database (compartilhados)
│
├── contexts/
│   ├── identity/            # COMMODITY — Auth/JWT
│   ├── freelancer/          # CUSTOM — perfis especializados
│   ├── compliance_catalog/  # CUSTOM — catálogo regulatório
│   ├── matching/            # GENESIS — algoritmo proprietário
│   ├── contracting/         # PRODUCT — contratos + assinatura digital
│   └── payment/             # COMMODITY — processamento de pagamentos
│
└── main.py                  # Composição da aplicação
```

Cada contexto segue a estrutura:
```
context/
├── domain/
│   ├── entities.py          # Aggregate Roots e Entities
│   ├── value_objects.py     # Value Objects (imutáveis)
│   └── events.py            # Domain Events
├── application/
│   ├── services.py          # Application Services (casos de uso)
│   └── commands.py          # Commands (entrada dos casos de uso)
├── infrastructure/
│   └── repository.py        # Implementação de Repository
└── api/
    └── router.py            # FastAPI Router (adaptador HTTP)
```

---

## Setup e Execução

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar
uvicorn main:app --reload

# Acessar documentação interativa
# http://localhost:8000/docs
```

---

## Fluxo de Valor Completo — Exemplo

```bash
# 1. Registrar freelancer especialista em LGPD
POST /freelancers/
{
  "user_id": "usr_001",
  "full_name": "Ana Lima",
  "headline": "Especialista LGPD & BACEN | 8 anos",
  "hourly_rate_brl": 350,
  "years_of_experience": 8,
  "availability_hours_per_week": 20,
  "max_complexity_level": 4
}

# 2. Adicionar especializações regulatórias
POST /freelancers/{id}/specializations
{ "specialization_code": "LGPD", "regulatory_body": "ANPD" }

# 3. Consultar catálogo regulatório
GET /compliance-catalog/frameworks?category=DATA_PROTECTION

# 4. Executar matching
POST /matching/
{
  "client_id": "cli_001",
  "framework_codes": ["LGPD"],
  "jurisdiction_codes": ["BR"],
  "min_experience_years": 5,
  "weekly_hours_needed": 10,
  "complexity_level": 3,
  "freelancer_profiles": [...]   # ACL: virá do contexto Freelancer
}
# → Retorna freelancers ranqueados por score de compatibilidade

# 5. Aceitar match e criar contrato
PATCH /matching/{match_id}/accept
POST /contracts/
{ "match_id": "...", "amount_brl": 15000, ... }

# 6. Assinar contrato (cliente e freelancer)
PATCH /contracts/{id}/sign  { "signer_role": "client" }
PATCH /contracts/{id}/sign  { "signer_role": "freelancer" }

# 7. Concluir contrato e processar pagamento
PATCH /contracts/{id}/complete
POST /payments/
{ "contract_id": "...", "gross_amount": 15000, "method_type": "pix" }
# → platform_fee: R$ 1.500 | net_amount (freelancer): R$ 13.500
```

---

## Referências

- Kaiser, S. (2022). *Adaptive Systems with Domain-Driven Design, Wardley Mapping, and Team Topologies*. Addison-Wesley.
- Evans, E. (2003). *Domain-Driven Design: Tackling Complexity in the Heart of Software*. Addison-Wesley.
- Skelton, M. & Pais, M. (2019). *Team Topologies*. IT Revolution Press.
- Ward, S. (2016). *Wardley Maps*. [medium.com/wardleymaps]