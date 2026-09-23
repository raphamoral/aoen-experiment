# Certifica

Plataforma de certificação digital de cursos livres com verificação pública.

## Funcionalidades

- Cadastro e login de alunos
- Listagem de cursos com inscrição
- Emissão de certificados PDF com QR code
- Verificação pública de autenticidade via URL única
- Painel admin para criar cursos e concluir inscrições

## Instalação

```bash
pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:5000

## Credenciais admin padrão

| Campo | Valor |
|-------|-------|
| E-mail | admin@certifica.com |
| Senha | admin123 |

Troque a senha após o primeiro login editando o banco de dados.

## Fluxo de uso

1. **Admin** cria um curso no painel `/admin`
2. **Aluno** se cadastra, faz login e se inscreve no curso
3. **Admin** acessa `/admin`, vê as inscrições pendentes e clica em "Concluir e Emitir Certificado"
4. **Aluno** acessa "Meus Certificados", baixa o PDF e compartilha o link de verificação
5. Qualquer pessoa acessa `/verify/<CODIGO>` e confirma a autenticidade

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `SECRET_KEY` | Chave secreta do Flask | valor fixo de dev |

Em produção, defina `SECRET_KEY` com um valor aleatório e seguro:

```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

## Banco de dados

SQLite local (`certifica.db`), criado automaticamente na primeira execução.

## Estrutura do certificado PDF

- Código único de 20 caracteres (SHA-256 com salt aleatório)
- QR code apontando para a URL de verificação pública
- Dados: nome do aluno, curso, instrutor, carga horária, data de emissão