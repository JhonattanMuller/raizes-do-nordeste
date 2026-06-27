"""Rotas de pedidos (fluxo crítico)."""
from fastapi import APIRouter, Depends, status

from app.api.presenters import pedido_out
from app.application.services.pedido_service import PedidoService
from app.core.deps import (
    CurrentUser,
    PageDep,
    get_pedido_service,
    require_roles,
)
from app.domain.enums import CanalPedido, Role, StatusPedido
from app.schemas.pedido import (
    AtualizarStatusRequest,
    PedidoCreate,
    PedidoResponse,
)

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

# Papéis operacionais que podem mudar status / cancelar.
_OPERACAO = (
    Role.ATENDENTE.value, Role.COZINHA.value, Role.GERENTE.value, Role.ADMIN.value,
)


@router.post(
    "", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED,
    summary="Criar pedido",
)
def criar(
    payload: PedidoCreate, user: CurrentUser,
    service: PedidoService = Depends(get_pedido_service),
):
    pedido = service.criar(
        user_id=user.get("uid"), unidade_id=payload.unidade_id,
        canal=payload.canal_pedido,
        itens_input=[i.model_dump() for i in payload.itens],
    )
    return pedido_out(pedido)


@router.get(
    "", response_model=list[PedidoResponse],
    summary="Listar pedidos (filtros: canalPedido, status, unidadeId)",
)
def listar(
    user: CurrentUser, page: PageDep,
    canalPedido: CanalPedido | None = None,
    status: StatusPedido | None = None,
    unidadeId: int | None = None,
    service: PedidoService = Depends(get_pedido_service),
):
    pedidos = service.listar(
        canal=canalPedido, status=status, unidade_id=unidadeId,
        offset=page.offset, limit=page.limit,
    )
    return [pedido_out(p) for p in pedidos]


@router.get("/{pedido_id}", response_model=PedidoResponse, summary="Obter pedido")
def obter(
    pedido_id: int, user: CurrentUser,
    service: PedidoService = Depends(get_pedido_service),
):
    return pedido_out(service.obter(pedido_id))


@router.patch(
    "/{pedido_id}/status", response_model=PedidoResponse,
    summary="Atualizar status (operação: ATENDENTE/COZINHA/GERENTE/ADMIN)",
)
def atualizar_status(
    pedido_id: int, payload: AtualizarStatusRequest,
    user=Depends(require_roles(*_OPERACAO)),
    service: PedidoService = Depends(get_pedido_service),
):
    return pedido_out(
        service.atualizar_status(pedido_id, payload.status, user.get("uid"))
    )


@router.post(
    "/{pedido_id}/cancelar", response_model=PedidoResponse,
    summary="Cancelar pedido (repõe estoque se já pago)",
)
def cancelar(
    pedido_id: int, user: CurrentUser,
    service: PedidoService = Depends(get_pedido_service),
):
    return pedido_out(service.cancelar(pedido_id, user.get("uid")))
