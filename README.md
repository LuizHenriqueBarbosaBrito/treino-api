# Treino API

API REST para catalogar **exercícios físicos por grupo muscular**. Permite que qualquer pessoa consulte o catálogo e que usuários autenticados cadastrem, atualizem e removam exercícios e grupos musculares.

Projeto da Atividade Prática de **Arquitetura e Desenvolvimento de APIs** (UNINTER, 2026).

## Tecnologias

| Item | Escolha |
|---|---|
| Linguagem | Python 3.10+ |
| Framework | FastAPI |
| Banco de dados | SQLite (arquivo `treino.db`; troca por PostgreSQL via `DATABASE_URL`) |
| ORM | SQLAlchemy 2.0 |
| Validação | Pydantic v2 |
| Autenticação | JWT (PyJWT) + senhas com bcrypt |
| Documentação | Swagger UI / OpenAPI (automático) |
| Testes | pytest + TestClient (httpx) |

## Pré-requisitos

- Python 3.10 ou superior
- `pip`
- Git

## Instalação

```bash
git clone <URL_DO_REPOSITORIO>
cd treino-api

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Configuração (variáveis de ambiente)

```bash
cp .env.example .env             # Windows: copy .env.example .env
```

Edite o `.env` e defina ao menos a `SECRET_KEY`. Para gerar uma:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

| Variável | Descrição | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave de assinatura do JWT (**obrigatória**) | — |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token | `60` |
| `DATABASE_URL` | String de conexão do banco | `sqlite:///./treino.db` |
| `CORS_ORIGINS` | Origens permitidas, separadas por vírgula | `http://localhost:3000` |

## Banco de dados

As tabelas são criadas **automaticamente** na primeira execução (`create_all` do SQLAlchemy). Não há passos manuais.
O arquivo `scripts/schema.sql` traz o script SQL equivalente, caso queira criar o banco manualmente.

## Executando

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- OpenAPI (JSON): http://localhost:8000/openapi.json

## Testes automatizados

```bash
pytest -v
```

São 20 testes que cobrem CRUD, filtros, validação, códigos HTTP, autenticação e CORS. Usam um banco SQLite separado (`test_treino.db`), apagado ao final.

## Endpoints

| Método | Endpoint | Finalidade | Autenticação | Respostas |
|---|---|---|---|---|
| POST | `/auth/register` | Criar usuário | Não | 201 / 400 / 409 |
| POST | `/auth/login` | Obter token JWT | Não | 200 / 401 |
| GET | `/auth/me` | Dados do usuário logado | **Sim** | 200 / 401 |
| GET | `/grupos` | Listar grupos musculares | Não | 200 |
| POST | `/grupos` | Criar grupo | **Sim** | 201 / 400 / 401 / 409 |
| DELETE | `/grupos/{id}` | Excluir grupo | **Sim** | 204 / 401 / 404 / 409 |
| GET | `/exercicios` | Listar (filtros: `grupo_id`, `nivel`, `busca`, `skip`, `limit`) | Não | 200 / 400 |
| GET | `/exercicios/{id}` | Consultar um exercício | Não | 200 / 404 |
| POST | `/exercicios` | Criar exercício | **Sim** | 201 / 400 / 401 / 409 |
| PATCH | `/exercicios/{id}` | Atualizar parcialmente | **Sim** | 200 / 400 / 401 / 404 / 409 |
| DELETE | `/exercicios/{id}` | Excluir exercício | **Sim** | 204 / 401 / 404 |

## Como testar a autenticação

1. Registre um usuário (use a senha que preferir, com 8+ caracteres):
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"seu_usuario","password":"sua_senha_aqui"}'
   ```
2. Faça login e copie o `access_token`:
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -d "username=seu_usuario&password=sua_senha_aqui"
   ```
3. Use o token nas rotas protegidas:
   ```bash
   curl http://localhost:8000/auth/me -H "Authorization: Bearer <TOKEN>"
   ```

No **Swagger UI**, clique em **Authorize**, informe usuário e senha e todas as rotas protegidas passam a funcionar.

## Exemplo completo

```bash
# criar grupo
curl -X POST http://localhost:8000/grupos \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"nome":"Peitoral"}'

# criar exercício
curl -X POST http://localhost:8000/exercicios \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"nome":"Supino reto","equipamento":"Barra","nivel":"iniciante","grupo_muscular_id":1}'

# listar com filtro
curl "http://localhost:8000/exercicios?nivel=iniciante&busca=supino"
```

## Formato de erros

Todos os erros seguem o mesmo padrão JSON:

```json
{ "erro": "Dados inválidos.", "detalhes": [ { "campo": "series_padrao", "mensagem": "Input should be less than or equal to 10" } ] }
```

## Estrutura do projeto

```
app/
  main.py          # app, CORS, tratamento global de erros
  config.py        # variáveis de ambiente
  database.py      # engine/sessão do SQLAlchemy
  models.py        # modelos ORM (tabelas)
  schemas.py       # validação e serialização (Pydantic)
  security.py      # bcrypt e JWT
  deps.py          # dependências (sessão, usuário autenticado)
  routers/         # auth, grupos, exercicios
tests/             # testes automatizados
scripts/schema.sql # script SQL do banco
docs/              # relatório técnico e evidências
```
