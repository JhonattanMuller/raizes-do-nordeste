"""T06-T10: criação de pedido, validações e regras de estoque/canal."""


def _criar(client, headers, unidade=1, produto=1, qtd=2, canal="TOTEM"):
    return client.post("/pedidos", headers=headers, json={
        "canalPedido": canal, "unidadeId": unidade,
        "itens": [{"produtoId": produto, "quantidade": qtd}],
    })


def test_t06_criar_pedido_valido_201(client, cliente_headers):
    r = _criar(client, cliente_headers)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "AGUARDANDO_PAGAMENTO"
    assert body["total"] > 0 and body["canalPedido"] == "TOTEM"


def test_t07_canal_pedido_ausente_422(client, cliente_headers):
    r = client.post("/pedidos", headers=cliente_headers, json={
        "unidadeId": 1, "itens": [{"produtoId": 1, "quantidade": 1}],
    })
    assert r.status_code == 422
    assert r.json()["error"] == "VALIDACAO"


def test_t08_unidade_inexistente_404(client, cliente_headers):
    r = _criar(client, cliente_headers, unidade=999)
    assert r.status_code == 404
    assert r.json()["error"] == "UNIDADE_NAO_ENCONTRADA"


def test_t09_estoque_insuficiente_409(client, cliente_headers):
    r = _criar(client, cliente_headers, produto=1, qtd=999999)
    assert r.status_code == 409
    assert r.json()["error"] == "ESTOQUE_INSUFICIENTE"


def test_t10_filtro_por_canal(client, cliente_headers):
    _criar(client, cliente_headers, canal="WEB", produto=3, qtd=1)
    r = client.get("/pedidos?canalPedido=WEB", headers=cliente_headers)
    assert r.status_code == 200
    assert all(p["canalPedido"] == "WEB" for p in r.json())


def test_t11_transicao_status_invalida_422(client, cliente_headers, admin_headers):
    pid = _criar(client, cliente_headers, produto=2, qtd=1).json()["pedidoId"]
    r = client.patch(f"/pedidos/{pid}/status", headers=admin_headers,
                     json={"status": "ENTREGUE"})
    assert r.status_code == 422
    assert r.json()["error"] == "TRANSICAO_STATUS_INVALIDA"
