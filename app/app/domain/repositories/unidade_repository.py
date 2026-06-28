"""Porta (interface) do repositório de Unidade."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.unidade import Unidade


class UnidadeRepository(ABC):
    @abstractmethod
    def add(self, unidade: Unidade) -> Unidade: ...

    @abstractmethod
    def get_by_id(self, unidade_id: int) -> Unidade | None: ...

    @abstractmethod
    def list(self, offset: int = 0, limit: int = 10) -> list[Unidade]: ...
