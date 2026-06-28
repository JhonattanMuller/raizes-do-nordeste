"""T12-T13: pagamento mock aprovado/recusado e efeitos no estoque."""


def _criar(client, headers, unidade=2, produto=4, qtd=2):
    return client.post("/pedidos", headers=headers, json={
        "canalPedido": "APP", "unidadeId": unidade,
        "itens": [{"produtoId": produto, "quantidade": qtd}],
    }).json()


def _estoque(client, unidade, produto):
    itens = client.get(f"/estoque/{unidade}").json()
    return next(e for e in itens if e["produtoId"] == produto)["quantidade"]


def test_t12_pagamento_aprovado_baixa_estoque(client, cliente_headers):
    antes = _estoque(client, 2, 4)
    pedido = _criar(client, cliente_headers, unidade=2, produto=4, qtd=2)
    r = client.post(f"/pagamentos/{pedido['pedidoId']}", headers=cliente_headers,
                    json={"aprovar": True})
    assert r.status_code == 201 and r.json()["status"] == "APROVADO"
    assert _estoque(client, 2, 4) == antes - 2


def test_t13_pagamento_recusado_nao_baixa(client, cliente_headers):
    antes = _estoque(client, 2, 5)
    pedido = _criar(client, cliente_headers, unidade=2, produto=5, qtd=1)
    r = client.post(f"/pagamentos/{pedido['pedidoId']}", headers=cliente_headers,
                    json={"aprovar": False})
    assert r.json()["status"] == "RECUSADO"
    assert _estoque(client, 2, 5) == antes


def test_t14_pagamento_duplicado_409(client, cliente_headers):
    pedido = _criar(client, cliente_headers, unidade=2, produto=6, qtd=1)
    client.post(f"/pagamentos/{pedido['pedidoId']}", headers=cliente_headers,
                json={"aprovar": True})
    r = client.post(f"/pagamentos/{pedido['pedidoId']}", headers=cliente_headers,
                    json={"aprovar": True})
    assert r.status_code == 409 and r.json()["error"] == "PAGAMENTO_JA_PROCESSADO"
