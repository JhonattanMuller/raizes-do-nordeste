"""Entidade Pedido — aggregate root do fluxo crítico do sistema.

Concentra as invariantes de transição de status e o cálculo de total.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.core.exceptions import (
    PedidoSemItensError,
    TransicaoStatusInvalidaError,
)
from app.domain.entities.item_pedido import ItemPedido
from app.domain.enums import CanalPedido, StatusPedido
from app.domain.value_objects.money import Money

# Máquina de estados do pedido: de -> {destinos permitidos}
_TRANSICOES: dict[StatusPedido, set[StatusPedido]] = {
    StatusPedido.CRIADO: {StatusPedido.AGUARDANDO_PAGAMENTO, StatusPedido.CANCELADO},
    StatusPedido.AGUARDANDO_PAGAMENTO: {StatusPedido.PAGO, StatusPedido.CANCELADO},
    StatusPedido.PAGO: {StatusPedido.EM_PREPARO, StatusPedido.CANCELADO},
    StatusPedido.EM_PREPARO: {StatusPedido.PRONTO, StatusPedido.CANCELADO},
    StatusPedido.PRONTO: {StatusPedido.ENTREGUE},
    StatusPedido.ENTREGUE: set(),
    StatusPedido.CANCELADO: set(),
}

# Status nos quais o estoque já foi baixado (usado para repor ao cancelar).
_ESTOQUE_BAIXADO = {
    StatusPedido.PAGO,
    StatusPedido.EM_PREPARO,
    StatusPedido.PRONTO,
}


@dataclass
class Pedido:
    id: int | None
    user_id: int
    unidade_id: int
    canal_pedido: CanalPedido
    status: StatusPedido = StatusPedido.AGUARDANDO_PAGAMENTO
    itens: list[ItemPedido] = field(default_factory=list)
    created_at: datetime | None = None

    @classmethod
    def criar(
        cls,
        user_id: int,
        unidade_id: int,
        canal: CanalPedido,
        itens: list[ItemPedido],
    ) -> "Pedido":
        if not itens:
            raise PedidoSemItensError()
        return cls(
            id=None,
            user_id=user_id,
            unidade_id=unidade_id,
            canal_pedido=canal,
            status=StatusPedido.AGUARDANDO_PAGAMENTO,
            itens=list(itens),
        )

    @property
    def total(self) -> Money:
        total = Money(0)
        for item in self.itens:
            total = total + item.subtotal
        return total

    @property
    def estoque_foi_baixado(self) -> bool:
        return self.status in _ESTOQUE_BAIXADO

    def pode_transitar_para(self, novo: StatusPedido) -> bool:
        return novo in _TRANSICOES.get(self.status, set())

    def atualizar_status(self, novo: StatusPedido) -> None:
        if not self.pode_transitar_para(novo):
            raise TransicaoStatusInvalidaError(
                message=(
                    f"Não é possível ir de {self.status.value} "
                    f"para {novo.value}."
                )
            )
        self.status = novo

    def marcar_pago(self) -> None:
        self.atualizar_status(StatusPedido.PAGO)

    def cancelar(self) -> None:
        self.atualizar_status(StatusPedido.CANCELADO)
