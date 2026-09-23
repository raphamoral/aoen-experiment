# Plataforma de Certificação Digital de Cursos Livres

Implementação em Python / FastAPI seguindo **Hexagonal Architecture** (Ports & Adapters) de Alistair Cockburn.

---

## Por que Hexagonal Architecture?

Cockburn definiu a Arquitetura Hexagonal como a separação estrita entre o **interior** (lógica de negócio) e o **exterior** (infraestrutura, frameworks, I/O). A aplicação se comunica com o mundo externo exclusivamente por meio de **Ports** (interfaces abstratas) e **Adapters** (implementações concretas).

Isso garante:

- **Testabilidade total**: o domínio e o serviço de aplicação são testáveis sem banco de dados, SMTP ou HTTP.
- **Substituição de adapters**: trocar SQLite por PostgreSQL, SMTP por SendGrid, ou armazenamento local por S3 não exige alterar nenhuma linha de negócio.
- **Simetria**: o tratamento de sistemas externos é uniforme — HTTP, banco de dados, e-mail e filesystem são todos "o lado de fora".

---

## Estrutura do Projeto

```
.
├── domain/                  ← INSIDE: zero dependências externas
│   ├── entities/            ← Agregados e entidades do domínio
│   ├── value_objects/       ← Objetos de valor imutáveis
│   ├── events/              ← Eventos de domínio
│   └── exceptions.py        ← Exceções de negócio
│
├── ports/                   ← Fronteiras abstratas (interfaces ABC)
│   ├── inbound/             ← Driving side: casos de uso
│   └── outbound/            ← Driven side: contratos de infraestrutura
│
├── application/
│   └── services/
│       └── certificate_service.py   ← O hexágono: implementa todos os ports inbound
│                                       e depende apenas dos ports outbound
│
├── adapters/                ← OUTSIDE: implementações concretas
│   ├── inbound/
│   │   └── http/            ← Driving adapter: FastAPI router + schemas + DI
│   └── outbound/
│       ├── persistence/     ← Driven adapter: SQLAlchemy + SQLite
│       ├── hashing/         ← Driven adapter: SHA-256
│       ├── notification/    ← Driven adapter: SMTP
│       └── storage/         ← Driven adapter: sistema de arquivos local
│
├── main.py                  ← Ponto de entrada; inclui o router
└── requirements.txt
```

---

## Decisões Arquiteturais

### 1. Ports Inbound = Casos de Uso
Cada caso de uso é uma interface ABC (`IssueCertificatePort`, `VerifyCertificatePort`, etc.).  
O `CertificateApplicationService` implementa todas elas — qualquer driving adapter (HTTP, CLI, fila de mensagens) depende apenas da interface.

### 2. Ports Outbound = Contratos de Infraestrutura
`CertificateRepositoryPort`, `HashingServicePort`, `NotificationServicePort` e `CertificateStoragePort` são ABCs puras que o domínio e o serviço de aplicação conhecem.  
As implementações concretas (SQLAlchemy, SHA-256, SMTP, disco) vivem em `adapters/outbound/`.

### 3. Composition Root
`adapters/inbound/http/dependencies.py` é o único local que conhece as implementações concretas e faz a injeção de dependências via FastAPI `Depends`. Adapters sem estado (hashing, notificação, storage) são singletons; o repositório recebe a sessão de banco de dados por request.

### 4. Domínio Puro
`domain/` não importa nada além da stdlib Python. Sem SQLAlchemy, sem Pydantic, sem FastAPI.

### 5. Hash de Verificação Pública
O hash SHA-256 é gerado a partir de `{certificate_id, student_id, course_id, issued_at, issuer_name}` em JSON canônico (chaves ordenadas). Qualquer pessoa com o hash pode verificar a autenticidade sem autenticação.

---

## Como Executar

```bash
pip install -r requirements.txt

# Opcional: copie e ajuste as variáveis de ambiente
# cp .env.example .env

uvicorn main:app --reload
```

Variáveis de ambiente suportadas:

| Variável       | Padrão                         | Descrição                        |
|----------------|-------------------------------|----------------------------------|
| `DATABASE_URL` | `sqlite:///./certificates.db` | URL de conexão SQLAlchemy        |
| `BASE_URL`     | `http://localhost:8000`       | Prefixo da URL de verificação    |
| `SMTP_HOST`    | `localhost`                   | Host SMTP                        |
| `SMTP_PORT`    | `587`                         | Porta SMTP                       |
| `SMTP_USER`    | _(vazio)_                     | Usuário SMTP (sem → log apenas)  |
| `SMTP_PASSWORD`| _(vazio)_                     | Senha SMTP                       |
| `SMTP_SENDER`  | `noreply@certification.local` | Endereço remetente               |
| `STORAGE_DIR`  | `./certificates_storage`      | Diretório de artefatos           |

---

## Endpoints

| Método   | Rota                                  | Descrição                              |
|----------|---------------------------------------|----------------------------------------|
| `POST`   | `/api/v1/certificates`               | Emitir certificado                     |
| `GET`    | `/api/v1/certificates/{id}`          | Detalhes de um certificado             |
| `DELETE` | `/api/v1/certificates/{id}`          | Revogar certificado (body: `reason`)   |
| `GET`    | `/api/v1/students/{id}/certificates` | Listar certificados de um estudante    |
| `GET`    | `/api/v1/verify/{hash}`              | **Verificação pública** por hash       |
| `GET`    | `/health`                            | Health check                           |

Documentação interativa disponível em `/docs` (Swagger UI).

---

## Fluxo de Verificação Pública

```
Terceiro                   Driving Adapter          Hexagon              Driven Adapter
   |                        (HTTP router)         (App Service)         (SQLAlchemy repo)
   |--- GET /verify/{hash} -->|                        |                       |
   |                          |-- verify_by_hash() -->|                       |
   |                          |                        |-- find_by_hash() --->|
   |                          |                        |<-- Certificate -------|
   |                          |<-- VerificationResult -|                       |
   |<-- 200 JSON -------------|                        |                       |
```

---

## Trocando um Adapter

Para substituir o armazenamento local por Amazon S3, basta:

1. Criar `adapters/outbound/storage/s3_certificate_storage.py` implementando `CertificateStoragePort`.
2. Alterar `adapters/inbound/http/dependencies.py` para instanciar `S3CertificateStorage`.

Nenhum código de domínio ou de serviço de aplicação muda.

---

## Testes

Com a separação hexagonal, cada camada é testável de forma isolada:

```python
# Teste de unidade do serviço de aplicação — sem banco, sem HTTP
service = CertificateApplicationService(
    repository=InMemoryCertificateRepository(),   # test double
    hashing_service=SHA256HashingService(),
    notification_service=FakeNotificationService(),
    storage=FakeCertificateStorage(),
    base_url="http://test",
)