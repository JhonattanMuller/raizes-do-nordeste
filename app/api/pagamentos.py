"""Rotas de pagamento (mock)."""
from fastapi import APIRouter, Depends, status

from app.api.presenters import pagamento_out
from app.application.services.pagamento_service import PagamentoService
from app.core.deps import CurrentUser, get_pagamento_service
from app.schemas.pagamento import PagamentoRequest, PagamentoResponse

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])


@router.post(
    "/{pedido_id}", response_model=PagamentoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Processar pagamento mock de um pedido",
)
def processar(
    pedido_id: int, user: CurrentUser,
    payload: PagamentoRequest | None = None,
    service: PagamentoService = Depends(get_pagamento_service),
):
    aprovar = payload.aprovar if payload else None
    return pagamento_out(service.processar(pedido_id, aprovar=aprovar))
