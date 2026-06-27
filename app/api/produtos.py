"""Rotas de produtos (catálogo da rede)."""
from fastapi import APIRouter, Depends, status

from app.api.presenters import produto_out
from app.application.services.produto_service import ProdutoService
from app.core.deps import PageDep, get_produto_service, require_roles
from app.domain.enums import Role
from app.schemas.produto import ProdutoCreate, ProdutoResponse

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("", response_model=list[ProdutoResponse], summary="Listar produtos")
def listar(page: PageDep, service: ProdutoService = Depends(get_produto_service)):
    return [produto_out(p) for p in service.listar(page.offset, page.limit)]


@router.get("/{produto_id}", response_model=ProdutoResponse, summary="Obter produto")
def obter(produto_id: int, service: ProdutoService = Depends(get_produto_service)):
    return produto_out(service.obter(produto_id))


@router.post(
    "", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED,
    summary="Criar produto (ADMIN/GERENTE)",
)
def criar(
    payload: ProdutoCreate,
    _user=Depends(require_roles(Role.ADMIN.value, Role.GERENTE.value)),
    service: ProdutoService = Depends(get_produto_service),
):
    return produto_out(service.criar(payload.nome, payload.preco))
