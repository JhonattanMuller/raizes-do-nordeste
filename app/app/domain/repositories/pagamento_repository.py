"""Porta (interface) do repositório de Pagamento."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.pagamento import Pagamento


class PagamentoRepository(ABC):
    @abstractmethod
    def add(self, pagamento: Pagamento) -> Pagamento: ...

    @abstractmethod
    def get_by_pedido_id(self, pedido_id: int) -> Pagamento | None: ...
