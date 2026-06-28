"""Configuração de testes: banco SQLite isolado em arquivo local."""
import os
import uuid

import pytest

_DB_PATH = os.path.join(os.path.dirname(__file__), "test_raizes.db")
if os.path.exists(_DB_PATH):
    os.remove(_DB_PATH)
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_PATH}"
os.environ["AUTO_SEED"] = "false"

from fastapi.testclient import TestClient  # noqa: E402

from app.infrastructure.database import SessionLocal, init_db  # noqa: E402
from app.infrastructure.seed import run_seed  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    init_db()
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()
    yield
    if os.path.exists(_DB_PATH):
        os.remove(_DB_PATH)


@pytest.fixture()
def client():
    return TestClient(app)


def _token(client, email, senha):
    return client.post(
        "/auth/login", json={"email": email, "senha": senha}
    ).json()["accessToken"]


@pytest.fixture()
def cliente_headers(client):
    """Cliente novo (CLIENTE) com consentimento LGPD."""
    email = f"user_{uuid.uuid4().hex[:8]}@email.com"
    client.post("/auth/register", json={
        "nome": "Cliente Teste", "email": email, "senha": "123456",
        "consentimentoLgpd": True,
    })
    return {"Authorization": f"Bearer {_token(client, email, '123456')}"}


@pytest.fixture()
def admin_headers(client):
    """Admin do seed."""
    return {"Authorization": f"Bearer {_token(client, 'admin@raizes.com', 'admin123')}"}
