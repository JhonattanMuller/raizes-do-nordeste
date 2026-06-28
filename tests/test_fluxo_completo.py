"""T15: fluxo crítico completo + fidelidade + cancelamento com reposição."""


def _criar(client, headers, unidade=1, produto=1, qtd=1):
    return client.post("/pedidos", headers=headers, json={
        "canalPedido": "BALCAO", "unidadeId": unidade,
        "itens": [{"produtoId": produto, "quantidade": qtd}],
    }).json()


def test_t15_fluxo_completo_e_fidelidade(client, cliente_headers, admin_headers):
    pedido = _criar(client, cliente_headers, unidade=1, produto=2, qtd=1)
    pid = pedido["pedidoId"]
    assert client.post(f"/pagamentos/{pid}", headers=cliente_headers,
                       json={"aprovar": True}).json()["status"] == "APROVADO"
    for novo in ["EM_PREPARO", "PRONTO", "ENTREGUE"]:
        r = client.patch(f"/pedidos/{pid}/status", headers=admin_headers,
                         json={"status": novo})
        assert r.status_code == 200 and r.json()["status"] == novo
    # Fidelidade acumulou pontos (1 ponto por real).
    assert client.get("/fidelidade/saldo", headers=cliente_headers).json()["pontos"] > 0


def test_t16_cancelamento_repoe_estoque(client, cliente_headers):
    def estoque(u, p):
        return next(e for e in client.get(f"/estoque/{u}").json()
                    if e["produtoId"] == p)["quantidade"]
    antes = estoque(1, 3)
    pedido = _criar(client, cliente_headers, unidade=1, produto=3, qtd=2)
    pid = pedido["pedidoId"]
    client.post(f"/pagamentos/{pid}", headers=cliente_headers, json={"aprovar": True})
    assert estoque(1, 3) == antes - 2
    r = client.post(f"/pedidos/{pid}/cancelar", headers=cliente_headers)
    assert r.status_code == 200 and r.json()["status"] == "CANCELADO"
    assert estoque(1, 3) == antes  # estoque reposto


def test_t17_resgate_fidelidade(client, cliente_headers):
    # Gera saldo via compra e resgata.
    pedido = _criar(client, cliente_headers, unidade=1, produto=1, qtd=1)
    client.post(f"/pagamentos/{pedido['pedidoId']}", headers=cliente_headers,
                json={"aprovar": True})
    saldo = client.get("/fidelidade/saldo", headers=cliente_headers).json()["pontos"]
    r = client.post("/fidelidade/resgatar", headers=cliente_headers, json={"pontos": 5})
    assert r.status_code == 200 and r.json()["pontos"] == saldo - 5
