# Raízes do Nordeste — Backend API

API REST que simula o backend de uma **rede de lanchonetes multiunidade**, com
pedidos por múltiplos canais (**APP, WEB, TOTEM, BALCÃO, PICKUP**), **estoque por
unidade**, pagamento mock, programa de **fidelidade**, **autorização por perfil**
e **trilha de auditoria**. Construída em **Domain-Driven Design (DDD)**.

---

##  Tecnologias

Python 3.11+ · FastAPI · SQLAlchemy 2 · SQLite (Postgres opcional) · JWT
(python-jose) · bcrypt (passlib) · Pydantic v2 · Uvicorn · Pytest · Docker.

---

##  Execução

### Docker (recomendado)
```bash
docker compose up --build
```
Acesse o Swagger em http://127.0.0.1:8000/docs

### Local
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # opcional
uvicorn app.main:app --reload
```
Na primeira execução o banco é criado e populado (`AUTO_SEED=true`).

### Testes
```bash
pip install -r requirements.txt
pytest -q                       # 17 cenários (T01..T17)
```

---

##  Usuários do seed

| Papel    | E-mail                 | Senha       |
|----------|------------------------|-------------|
| ADMIN    | admin@raizes.com       | admin123    |
| GERENTE  | gerente@raizes.com     | gerente123  |
| ATENDENTE| atendente@raizes.com   | atend123    |

Clientes são criados via `POST /auth/register`. O seed também cria **2 unidades**,
**6 produtos** e **estoque inicial** (50 un. de cada produto em cada unidade).

---

## Documentação (Swagger/OpenAPI)

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

---

## Arquitetura (DDD)

```
API  →  APPLICATION  →  DOMAIN  ←  INFRASTRUCTURE
(rotas)   (casos de uso)  (regras)   (ORM/repos/seed)
```

- **domain/** — entidades ricas (Usuario, Unidade, Produto, EstoqueItem, Pedido,
  ItemPedido, Pagamento, Fidelidade), value objects (Money, Email), enums,
  exceções e **interfaces de repositório** (ports).
- **application/** — services: auth, unidade, produto, estoque, pedido, pagamento,
  fidelidade.
- **infrastructure/** — modelos ORM, mappers (ORM⇆domínio), repositórios
  SQLAlchemy, auditoria, seed.
- **api/** — routers FastAPI, schemas Pydantic (DTOs), presenters; autenticação e
  autorização por perfil.

A regra de dependência aponta sempre para o domínio. As entidades concentram as
invariantes (ex.: `Pedido` valida a máquina de estados; `EstoqueItem` impede
estoque negativo) e ficam livres de framework.

---

##  Autenticação e autorização

`POST /auth/register` e `POST /auth/login` (retorna `accessToken`). Rotas
protegidas exigem `Authorization: Bearer <token>`. Papéis:
`CLIENTE, ATENDENTE, COZINHA, GERENTE, ADMIN`.

| Ação                                   | Perfis            |
|----------------------------------------|-------------------|
| Criar pedido / pagar / fidelidade      | autenticado       |
| Atualizar status / cancelar pedido     | ATENDENTE/COZINHA/GERENTE/ADMIN |
| Criar produto / unidade / mov. estoque | GERENTE/ADMIN     |
| Auditoria                              | GERENTE/ADMIN     |

Acesso sem token → **401**; perfil sem permissão → **403**.

---

## Fluxo crítico

```
POST /pedidos  →  valida unidade, itens e estoque (da unidade); status AGUARDANDO_PAGAMENTO
POST /pagamentos/{pedidoId}  →  mock APROVADO/RECUSADO
        └─ se APROVADO: status → PAGO + baixa de estoque da unidade + pontos de fidelidade
PATCH /pedidos/{id}/status  →  EM_PREPARO → PRONTO → ENTREGUE
POST  /pedidos/{id}/cancelar →  CANCELADO (repõe estoque se já pago)
```

Máquina de estados: `AGUARDANDO_PAGAMENTO → PAGO → EM_PREPARO → PRONTO → ENTREGUE`,
com `CANCELADO` a partir dos estados não finais. Transições inválidas → **422**.

---

## Endpoints

| Método | Rota | Auth |
|--------|------|------|
| POST | `/auth/register` · `/auth/login` | público |
| GET | `/unidades` · `/unidades/{id}` · `/unidades/{id}/cardapio` | público |
| POST | `/unidades` | GERENTE/ADMIN |
| GET | `/produtos?page=&limit=` · `/produtos/{id}` | público |
| POST | `/produtos` | GERENTE/ADMIN |
| GET | `/estoque/{unidadeId}` | público |
| POST | `/estoque/{unidadeId}/movimentar` | GERENTE/ADMIN |
| POST | `/pedidos` | autenticado |
| GET | `/pedidos?canalPedido=&status=&unidadeId=&page=&limit=` | autenticado |
| GET | `/pedidos/{id}` | autenticado |
| PATCH | `/pedidos/{id}/status` | operação |
| POST | `/pedidos/{id}/cancelar` | autenticado |
| POST | `/pagamentos/{pedidoId}` | autenticado |
| GET | `/fidelidade/saldo` · POST `/fidelidade/resgatar` | autenticado |
| GET | `/auditoria` | GERENTE/ADMIN |

### Contrato (camelCase)
Criar pedido:
```json
{ "canalPedido": "TOTEM", "unidadeId": 1,
  "itens": [{ "produtoId": 1, "quantidade": 2 }], "formaPagamento": "MOCK" }
```

### Padrão de erro
```json
{ "error": "ESTOQUE_INSUFICIENTE",
  "message": "Não há quantidade suficiente para um ou mais itens.",
  "details": [{ "field": "produto_id:1", "issue": "Disponível: 1" }],
  "timestamp": "2026-06-23T12:00:00Z", "path": "/pedidos" }
```
Status codes: 200, 201, 400/422, 401, 403, 404, 409.

---

## LGPD e segurança

- Dados pessoais: nome (identificação), e-mail (login). Finalidade clara,
  minimização (nada além do necessário).
- Senha: somente **hash bcrypt**; `senha_hash` nunca aparece em respostas.
- **Consentimento obrigatório** no cadastro e para fidelidade.
- **Autorização por perfil** aplicada nos endpoints.
- **Auditoria**: criar pedido, mudar status, cancelar e pagamento são registrados.

---

## Modelo de dados (resumo)

```
USUARIO 1─N PEDIDO N─1 UNIDADE
PEDIDO 1─N ITEM_PEDIDO N─1 PRODUTO
UNIDADE 1─N ESTOQUE_UNIDADE N─1 PRODUTO   (estoque por unidade)
PEDIDO 1─1 PAGAMENTO
USUARIO 1─1 FIDELIDADE
AUDITORIA (registro de ações sensíveis)
```

---

## Evidências (preencher ao publicar)

- **Repositório:** _adicione o link público do GitHub/GitLab_
- **Swagger:** `http://127.0.0.1:8000/docs` (instruções acima)
- **Coleção Postman:** `raizes-nordeste.postman_collection.json` (na raiz do repo)
- Plano de testes detalhado: ver `docs/` e os PDFs de documentação.

---

## Decisões e lacunas

Ver `docs/ANALISE.md` e os PDFs em `docs/` (documentação técnica, guia para nova
entidade e roteiro de apresentação técnica).
