# FreelanceCompliance — Marketplace de Compliance Regulatório

Plataforma para conectar empresas com freelancers especializados em compliance regulatório (LGPD, GDPR, SOX, PCI-DSS, ISO 27001, etc.).

## Instalação

```bash
pip install -r requirements.txt
python app.py
```

A API sobe em `http://localhost:5000`. O banco SQLite (`marketplace.db`) é criado automaticamente.

---

## Rotas

### Auth
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/register` | Cria conta (role: `client` ou `freelancer`) |
| POST | `/login` | Login |
| POST | `/logout` | Logout |

**Registro:**
```json
{ "name": "Ana Lima", "email": "ana@empresa.com", "password": "senha123", "role": "client" }
```

---

### Freelancers
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/profile` | Criar/atualizar perfil (freelancer autenticado) |
| GET | `/freelancers` | Listar freelancers disponíveis |
| GET | `/freelancers/<id>` | Ver perfil completo + avaliações |

**Filtros em `/freelancers`:**
- `?specialization=LGPD` — filtra por especialização
- `?max_rate=200` — taxa horária máxima
- `?min_experience=3` — anos mínimos de experiência

**Criar perfil:**
```json
{
  "bio": "Especialista em LGPD e GDPR com 8 anos de experiência",
  "hourly_rate": 180.00,
  "specializations": "LGPD,GDPR,ISO 27001",
  "certifications": "CIPP/E, CIPM",
  "years_experience": 8,
  "linkedin": "https://linkedin.com/in/ana",
  "available": true
}
```

---

### Vagas
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/jobs` | Criar vaga (client) |
| GET | `/jobs` | Listar vagas |
| GET | `/jobs/<id>` | Ver vaga + propostas |
| GET | `/my-jobs` | Minhas vagas / vagas que me candidatei |
| PATCH | `/jobs/<id>/close` | Encerrar vaga (client dono) |

**Filtros em `/jobs`:**
- `?area=LGPD`
- `?status=open` (open / in_progress / closed)

**Criar vaga:**
```json
{
  "title": "Adequação LGPD para startup SaaS",
  "description": "Precisamos mapear dados pessoais e elaborar política de privacidade.",
  "area": "LGPD",
  "budget": 5000.00,
  "deadline": "2026-05-30"
}
```

---

### Propostas
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/jobs/<id>/proposals` | Enviar proposta (freelancer) |
| PATCH | `/proposals/<id>` | Aceitar/rejeitar proposta (client) |

**Enviar proposta:**
```json
{ "price": 4500.00, "delivery_days": 30, "cover_letter": "Tenho certificação CIPP/E e já realizei projetos similares..." }
```

**Atualizar proposta:**
```json
{ "status": "accepted" }
```
Ao aceitar uma proposta, as demais são automaticamente rejeitadas e a vaga passa para `in_progress`.

---

### Avaliações
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/reviews` | Avaliar usuário após trabalho |

```json
{ "reviewed_id": 5, "job_id": 2, "rating": 5, "comment": "Excelente trabalho, entrega antes do prazo." }
```

- Clientes avaliam freelancers e vice-versa
- Apenas participantes da vaga podem avaliar
- Freelancer só avalia se teve proposta aceita

---

## Fluxo Típico

```
1. Empresa cria conta (role: client)
2. Freelancer cria conta + preenche perfil (role: freelancer)
3. Empresa posta vaga
4. Freelancer encontra vaga e envia proposta
5. Empresa aceita proposta → vaga vai para in_progress
6. Trabalho concluído → empresa encerra vaga
7. Ambos se avaliam mutuamente
```

## Áreas de Compliance Suportadas

LGPD · GDPR · SOX · PCI-DSS · ISO 27001 · HIPAA · Basel III · BACEN · CVM · SUSEP · Compliance Trabalhista · Anticorrupção (Lei 12.846) · ESG · AML/KYC