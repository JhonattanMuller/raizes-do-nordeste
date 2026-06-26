"""Porta (interface) do repositório de Estoque por unidade."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.estoque_item import EstoqueItem


class EstoqueRepository(ABC):
    @abstractmethod
    def add(self, item: EstoqueItem) -> EstoqueItem: ...

    @abstractmethod
    def get(self, unidade_id: int, produto_id: int) -> EstoqueItem | None: ...

    @abstractmethod
    def update(self, item: EstoqueItem) -> EstoqueItem: ...

    @abstractmethod
    def list_por_unidade(self, unidade_id: int) -> list[EstoqueItem]: ...
