"""Ponto de entrada da aplicação FastAPI — Raízes do Nordeste Backend API."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import (
    auditoria,
    auth,
    estoque,
    fidelidade,
    pagamentos,
    pedidos,
    produtos,
    unidades,
)
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.infrastructure.database import SessionLocal, init_db
from app.infrastructure.seed import run_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if settings.auto_seed:
        db = SessionLocal()
        try:
            run_seed(db)
        finally:
            db.close()
    yield


DESCRIPTION = """
Backend de uma rede de lanchonetes multiunidade (APP, WEB, TOTEM, BALCÃO, PICKUP).

**Fluxo crítico:** criar pedido → pagamento mock → atualização de status, com
baixa automática de estoque **por unidade**, fidelização e trilha de auditoria.
Arquitetura em DDD (domínio, aplicação, infraestrutura e API).
"""

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=DESCRIPTION,
    lifespan=lifespan,
)

register_exception_handlers(app)

for r in (auth, unidades, produtos, estoque, pedidos, pagamentos, fidelidade, auditoria):
    app.include_router(r.router)


@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}
