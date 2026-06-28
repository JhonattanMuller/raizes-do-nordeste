"""T01-T05: autenticação, autorização e validação."""


def test_t01_login_valido(client):
    r = client.post("/auth/login", json={"email": "admin@raizes.com", "senha": "admin123"})
    assert r.status_code == 200
    body = r.json()
    assert "accessToken" in body and body["user"]["role"] == "ADMIN"


def test_t02_acesso_sem_token_401(client):
    r = client.get("/pedidos")
    assert r.status_code == 401
    assert r.json()["error"] == "NAO_AUTENTICADO"


def test_t03_perfil_sem_permissao_403(client, cliente_headers):
    # CLIENTE não pode criar produto (somente ADMIN/GERENTE).
    r = client.post("/produtos", headers=cliente_headers, json={"nome": "X", "preco": 5})
    assert r.status_code == 403
    assert r.json()["error"] == "SEM_PERMISSAO"


def test_t04_consentimento_lgpd_obrigatorio_422(client):
    r = client.post("/auth/register", json={
        "nome": "Sem", "email": "semlgpd@email.com", "senha": "123456",
        "consentimentoLgpd": False,
    })
    assert r.status_code == 422
    assert r.json()["error"] == "CONSENTIMENTO_LGPD_OBRIGATORIO"


def test_t05_login_credenciais_invalidas_401(client):
    r = client.post("/auth/login", json={"email": "admin@raizes.com", "senha": "errada"})
    assert r.status_code == 401
    assert r.json()["error"] == "CREDENCIAIS_INVALIDAS"
