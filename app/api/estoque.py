"""Rotas de estoque por unidade."""
from fastapi import APIRouter, Depends

from app.api.presenters import estoque_out
from app.application.services.estoque_service import EstoqueService
from app.core.deps import get_estoque_service, require_roles
from app.domain.enums import Role
from app.schemas.produto import EstoqueItemResponse, MovimentoEstoqueRequest

router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.get(
    "/{unidade_id}", response_model=list[EstoqueItemResponse],
    summary="Consultar estoque (saldo) de uma unidade",
)
def consultar(unidade_id: int, service: EstoqueService = Depends(get_estoque_service)):
    return [estoque_out(e) for e in service.consultar_unidade(unidade_id)]


@router.post(
    "/{unidade_id}/movimentar", response_model=EstoqueItemResponse,
    summary="Entrada/saída de estoque na unidade (ADMIN/GERENTE)",
)
def movimentar(
    unidade_id: int, payload: MovimentoEstoqueRequest,
    _user=Depends(require_roles(Role.ADMIN.value, Role.GERENTE.value)),
    service: EstoqueService = Depends(get_estoque_service),
):
    item = service.movimentar(
        unidade_id, payload.produto_id, payload.tipo.value, payload.quantidade
    )
    return estoque_out(item)