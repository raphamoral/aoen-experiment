# NutriLab IA

App de nutrição personalizada com IA baseada em exames laboratoriais. O paciente cadastra seus dados, insere os resultados dos exames e recebe um plano nutricional completo gerado pela IA.

## Requisitos

- Python 3.9+
- Chave de API da Anthropic

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

No Windows:
```cmd
set ANTHROPIC_API_KEY=sk-ant-...
```

## Execução

```bash
python app.py
```

Acesse: http://localhost:5000

## Funcionalidades

- **Cadastro de pacientes** — nome, idade, sexo, peso e altura
- **Envio de exames** — hemograma, bioquímica, hormônios tireoidianos, vitaminas, função hepática e renal
- **Plano nutricional por IA** — análise dos exames, diagnóstico nutricional, cardápio diário, suplementação e monitoramento
- **Histórico** — todos os planos gerados por paciente

## Exames suportados

Hemoglobina, hematócrito, leucócitos, plaquetas, VCM, ferritina, glicose, HbA1c, colesterol total, HDL, LDL, triglicerídeos, TSH, T4 livre, vitamina D, vitamina B12, zinco, magnésio, TGO, TGP, creatinina, ureia, ácido úrico e PCR.

## Estrutura

```
app.py          — toda a aplicação (rotas, lógica, banco, frontend)
requirements.txt
nutri.db        — banco SQLite criado automaticamente