"""Porta (interface) do repositório de Pedido."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.pedido import Pedido
from app.domain.enums import CanalPedido, StatusPedido


class PedidoRepository(ABC):
    @abstractmethod
    def add(self, pedido: Pedido) -> Pedido: ...

    @abstractmethod
    def get_by_id(self, pedido_id: int) -> Pedido | None: ...

    @abstractmethod
    def update(self, pedido: Pedido) -> Pedido: ...

    @abstractmethod
    def list(
        self,
        canal: CanalPedido | None = None,
        status: StatusPedido | None = None,
        unidade_id: int | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[Pedido]: ...
