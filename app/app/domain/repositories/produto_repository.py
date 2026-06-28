"""Porta (interface) do repositório de Produto."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.produto import Produto


class ProdutoRepository(ABC):
    @abstractmethod
    def add(self, produto: Produto) -> Produto: ...

    @abstractmethod
    def get_by_id(self, produto_id: int) -> Produto | None: ...

    @abstractmethod
    def list(self, offset: int = 0, limit: int = 10) -> list[Produto]: ...

    @abstractmethod
    def update(self, produto: Produto) -> Produto: ...
