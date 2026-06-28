"""Rotas de unidades da rede e cardápio por unidade."""
from fastapi import APIRouter, Depends, status

from app.api.presenters import estoque_out, unidade_out
from app.application.services.unidade_service import UnidadeService
from app.core.deps import PageDep, get_unidade_service, require_roles
from app.domain.enums import Role
from app.schemas.produto import EstoqueItemResponse
from app.schemas.unidade import UnidadeCreate, UnidadeResponse

router = APIRouter(prefix="/unidades", tags=["Unidades"])


@router.get("", response_model=list[UnidadeResponse], summary="Listar unidades")
def listar(page: PageDep, service: UnidadeService = Depends(get_unidade_service)):
    return [unidade_out(u) for u in service.listar(page.offset, page.limit)]


@router.get("/{unidade_id}", response_model=UnidadeResponse, summary="Obter unidade")
def obter(unidade_id: int, service: UnidadeService = Depends(get_unidade_service)):
    return unidade_out(service.obter(unidade_id))


@router.get(
    "/{unidade_id}/cardapio", response_model=list[EstoqueItemResponse],
    summary="Cardápio (itens com estoque) da unidade",
)
def cardapio(unidade_id: int, service: UnidadeService = Depends(get_unidade_service)):
    return [estoque_out(e) for e in service.cardapio(unidade_id)]


@router.post(
    "", response_model=UnidadeResponse, status_code=status.HTTP_201_CREATED,
    summary="Criar unidade (ADMIN/GERENTE)",
)
def criar(
    payload: UnidadeCreate,
    _user=Depends(require_roles(Role.ADMIN.value, Role.GERENTE.value)),
    service: UnidadeService = Depends(get_unidade_service),
):
    return unidade_out(service.criar(payload.nome, payload.cidade))
