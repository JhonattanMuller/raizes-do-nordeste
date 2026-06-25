"""Dependências do FastAPI: sessão de DB, services, paginação e auth/roles."""
from typing import Annotated

from fastapi import Depends, Header, Query
from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.application.services.estoque_service import EstoqueService
from app.application.services.fidelidade_service import FidelidadeService
from app.application.services.pagamento_service import PagamentoService
from app.application.services.pedido_service import PedidoService
from app.application.services.produto_service import ProdutoService
from app.application.services.unidade_service import UnidadeService
from app.core.exceptions import NaoAutenticadoError, SemPermissaoError
from app.core.security import decode_access_token
from app.infrastructure.database import SessionLocal
from app.infrastructure.repositories.auditoria_repository_impl import (
    SQLAuditoriaRepository,
)
from app.infrastructure.repositories.estoque_repository_impl import (
    SQLEstoqueRepository,
)
from app.infrastructure.repositories.fidelidade_repository_impl import (
    SQLFidelidadeRepository,
)
from app.infrastructure.repositories.pagamento_repository_impl import (
    SQLPagamentoRepository,
)
from app.infrastructure.repositories.pedido_repository_impl import (
    SQLPedidoRepository,
)
from app.infrastructure.repositories.produto_repository_impl import (
    SQLProdutoRepository,
)
from app.infrastructure.repositories.unidade_repository_impl import (
    SQLUnidadeRepository,
)
from app.infrastructure.repositories.usuario_repository_impl import (
    SQLUsuarioRepository,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDep = Annotated[Session, Depends(get_db)]


# ---------- Paginação ----------
class Pagination:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
    ):
        self.page = page
        self.limit = limit
        self.offset = (page - 1) * limit


PageDep = Annotated[Pagination, Depends(Pagination)]


# ---------- Fábricas de services ----------
def get_auth_service(db: DbDep) -> AuthService:
    return AuthService(SQLUsuarioRepository(db))


def get_produto_service(db: DbDep) -> ProdutoService:
    return ProdutoService(SQLProdutoRepository(db))


def get_unidade_service(db: DbDep) -> UnidadeService:
    return UnidadeService(SQLUnidadeRepository(db), SQLEstoqueRepository(db))


def get_estoque_service(db: DbDep) -> EstoqueService:
    return EstoqueService(
        SQLEstoqueRepository(db), SQLProdutoRepository(db), SQLUnidadeRepository(db)
    )


def get_fidelidade_service(db: DbDep) -> FidelidadeService:
    return FidelidadeService(SQLFidelidadeRepository(db), SQLUsuarioRepository(db))


def get_pedido_service(db: DbDep) -> PedidoService:
    return PedidoService(
        SQLPedidoRepository(db),
        SQLProdutoRepository(db),
        SQLUnidadeRepository(db),
        get_estoque_service(db),
        SQLAuditoriaRepository(db),
    )


def get_pagamento_service(db: DbDep) -> PagamentoService:
    return PagamentoService(
        SQLPagamentoRepository(db),
        SQLPedidoRepository(db),
        get_estoque_service(db),
        get_fidelidade_service(db),
        SQLAuditoriaRepository(db),
    )


# ---------- Autenticação / Autorização ----------
def get_current_user(
    db: DbDep, authorization: Annotated[str | None, Header()] = None
) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise NaoAutenticadoError(message="Token ausente.")
    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    if not payload:
        raise NaoAutenticadoError(message="Token inválido ou expirado.")
    return payload


CurrentUser = Annotated[dict, Depends(get_current_user)]


def require_roles(*roles: str):
    """Dependência de autorização: exige que o usuário tenha um dos papéis."""

    def _checker(user: CurrentUser) -> dict:
        if roles and user.get("role") not in roles:
            raise SemPermissaoError(
                message=f"Requer papel: {', '.join(roles)}.",
                details=[{"field": "role", "issue": f"atual: {user.get('role')}"}],
            )
        return user

    return _checker
