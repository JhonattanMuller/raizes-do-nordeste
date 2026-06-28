"""Rotas de auditoria (logs de ações sensíveis) — ADMIN/GERENTE."""
from fastapi import APIRouter, Depends

from app.core.deps import DbDep, PageDep, require_roles
from app.domain.enums import Role
from app.infrastructure.repositories.auditoria_repository_impl import (
    SQLAuditoriaRepository,
)

router = APIRouter(prefix="/auditoria", tags=["Auditoria"])


@router.get("", summary="Listar logs de ações sensíveis (ADMIN/GERENTE)")
def listar(
    db: DbDep, page: PageDep,
    _user=Depends(require_roles(Role.ADMIN.value, Role.GERENTE.value)),
):
    return SQLAuditoriaRepository(db).listar(offset=page.offset, limit=page.limit)
