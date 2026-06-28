# 🔎 Relatório de Análise — Lacunas e Decisões de Projeto

Este documento registra os **pontos soltos** encontrados nos arquivos
`project.docx` e `Projeto.docx`, ou seja, partes do fluxo que **precisavam
existir** mas não estavam (ou estavam apenas parcialmente) documentadas. Para
cada item há a decisão tomada na implementação.

> Resumo: a especificação descreve bem o *quê* (entidades, fluxo, regras), mas
> deixa lacunas no *como* (contratos de API, autenticação real, atomicidade,
> validações). Abaixo, o que foi completado para o sistema funcionar de ponta a
> ponta.

---

## 1. Inconsistências entre os dois documentos

| Item | `project.docx` | `Projeto.docx` | Decisão |
|------|----------------|----------------|---------|
| Status inicial do pedido | Fluxo `CRIADO → PAGO → ...` | `criar_pedido` define `AGUARDANDO_PAGAMENTO` | Pedido nasce em **`AGUARDANDO_PAGAMENTO`**; `CRIADO` e `CANCELADO` existem no enum para flexibilidade. |
| Campo do canal no body | `"canal"` | `canal_pedido` (coluna) | Body usa **`canal`**; persistência usa `canal_pedido`. Filtro de listagem usa `canalPedido` (querystring), como no Postman do enunciado. |
| Enum de canais | `APP` (exemplos) | `APP, TOTEM, BALCAO, PICKUP, WEB` | Adotado o conjunto **completo** do `Projeto.docx`. |
| Status HTTP de criação | testes esperam `200` | — | Padronizado em **`201 Created`** para criações (REST). *(Observação: o teste de exemplo do enunciado usava 200; ajustado para 201.)* |

---

## 2. Lacunas funcionais (estava no fluxo, faltava no documento)

1. **Endpoint de atualização de status** — o README cita
   `PATCH /pedidos/{id}/status`, mas não havia código nem regras. **Implementado**
   com uma **máquina de estados** que recusa transições inválidas
   (`TRANSICAO_STATUS_INVALIDA`).

2. **Endpoint de pagamento** — citado como `POST /pagamentos/{pedido_id}`, mas o
   `Projeto.docx` só trazia a função `dar_baixa_estoque` (inclusive **duplicada**,
   rotulada como "pagamento mock" e como "estoque real"). **Implementado** o
   serviço de pagamento que: cria o pagamento, e **se aprovado** marca o pedido
   como `PAGO` e dá baixa no estoque.

3. **Produtos sem CRUD** — `Produto` é central (preço/estoque), mas não havia
   como criá-los/listá-los. **Implementados** `GET /produtos`, `GET /produtos/{id}`
   e `POST /produtos`, mais um **seed** inicial.

4. **Estoque sem endpoints** — havia regra de baixa, mas nenhuma forma de
   **consultar** ou **repor** estoque. **Implementados** `GET /estoque` e
   `POST /estoque/{id}/repor`.

5. **Momento da baixa de estoque ambíguo** — o documento validava estoque na
   criação, mas a baixa aparecia solta. **Decisão:** valida na **criação** (não
   permite pedido sem estoque) e **baixa apenas no pagamento aprovado**, evitando
   reservar estoque de pedidos nunca pagos.

6. **Pagamento duplicado** — não previsto. **Implementada** a regra: um pedido só
   pode ser pago uma vez (`PAGAMENTO_JA_PROCESSADO`).

---

## 3. Segurança / Autenticação

1. **JWT não era usado para proteger rotas** — o `Projeto.docx` gerava o token no
   login, mas **nenhuma rota o exigia**. **Implementada** a dependência
   `get_current_user` que valida o `Bearer token`; rotas de escrita/consulta de
   pedidos passam a exigir autenticação.

2. **`user_id` vinha no corpo do pedido** — risco de um usuário criar pedido em
   nome de outro. **Decisão:** o `user_id` é extraído **do token** (claim `uid`),
   não do body.

3. **`SECRET_KEY` fixa no código** — **movida** para variável de ambiente
   (`app/core/config.py`), com aviso de troca em produção.

4. **Senha sem validação de tamanho** — adicionada validação mínima nos schemas.
   *(Política de senha forte fica como melhoria futura.)*

5. **Roles definidas mas sem uso (`CLIENTE/ATENDENTE/ADMIN`)** — a infraestrutura
   está pronta (claim `role` no token), porém **autorização por papel** (ex.:
   só ADMIN cria produto / muda status) **não foi exigida** no enunciado. Hoje
   qualquer usuário autenticado acessa as rotas protegidas — ver "Melhorias".

---

## 4. Integridade de dados e transações

1. **Atomicidade do pagamento** — criar pagamento, mudar status e baixar estoque
   são operações que, idealmente, deveriam ocorrer em **uma única transação**
   (padrão *Unit of Work*). Na implementação atual cada repositório faz `commit`
   individual. Para um projeto acadêmico é aceitável, mas em produção uma falha
   no meio poderia deixar estado inconsistente. **Registrado como melhoria.**

2. **Concorrência de estoque** — dois pedidos simultâneos do mesmo produto podem
   passar pela validação antes da baixa (condição de corrida). Solução real:
   bloqueio otimista/pessimista no banco. **Fora do escopo**, registrado.

3. **Preço congelado no item** — o preço unitário é gravado no `ItemPedido` no
   momento do pedido, então alterações futuras de preço **não** afetam pedidos
   antigos. (Decisão de modelagem; não estava no documento.)

4. **Valores monetários** — o documento usava `float`. **Decisão:** Value Object
   `Money` em **centavos (int)** para evitar erros de arredondamento.

---

## 5. Validação e contratos de API

1. **Bodies eram `dict` solto** (`def criar(data: dict)`) — sem validação. **Substituídos**
   por **schemas Pydantic** com exemplos, validação de tipos, e-mail e limites
   (quantidade > 0, preço > 0, etc.).

2. **DER incompleto** — o `ITEM_PEDIDO` não trazia preço, e `PAGAMENTO` não tinha
   `valor`. **Adicionados** `preco_unitario_cents` (item) e `valor_cents`
   (pagamento). O relacionamento "PRODUTO 1—1 ESTOQUE" foi simplificado: o
   estoque é um **atributo do Produto** (não há entidade Estoque separada), o que
   é coerente com o restante do documento.

3. **Datas/timestamps** — não há `created_at`/`updated_at` em nenhuma entidade.
   Úteis para auditoria/LGPD. **Registrado como melhoria** (não exigido).

---

## 6. Pontos de LGPD que faltavam operacionalizar

- O documento declara o uso dos dados, mas **não exigia o consentimento na
  prática**. **Implementado:** cadastro só prossegue com `consentimento_lgpd:
  true`.
- **Faltam** (registrados como melhoria, pois não exigidos): endpoint de
  exclusão/anonimização de dados ("direito ao esquecimento"), exportação de
  dados do titular e data/registro do consentimento.

---

## 7. Itens não cobertos (melhorias futuras sugeridas)

Nenhum destes era exigido pelo enunciado; ficam como recomendação:

- **Unit of Work / transação única** no fluxo de pagamento.
- **Autorização por papel (RBAC)** usando o claim `role`.
- **Migrations** (Alembic) em vez de `create_all`.
- **Refresh token** e expiração/renovação de sessão.
- **Timestamps e soft-delete** para auditoria e LGPD.
- **Paginação** na listagem de pedidos/produtos.
- **Rate limiting** e CORS configurável.
- **Logs estruturados** e observabilidade.
- **Controle de concorrência** de estoque.

---

## 8. Resumo do que foi entregue além do documento

✅ Autenticação JWT realmente aplicada às rotas
✅ Endpoint e máquina de estados de status do pedido
✅ Serviço de pagamento mock completo + baixa de estoque condicionada à aprovação
✅ CRUD de produtos e endpoints de estoque
✅ Seed automático (6 produtos + admin)
✅ Validação via Pydantic e padrão de erro unificado
✅ Value Objects (Money/Email) e entidades de domínio ricas
✅ Suíte de testes (12 casos) + coleção Postman
✅ Docker / Docker Compose (SQLite por padrão, Postgres opcional)
