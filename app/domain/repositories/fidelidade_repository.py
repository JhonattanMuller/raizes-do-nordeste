"""Porta (interface) do repositório de Fidelidade."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.fidelidade import Fidelidade


class FidelidadeRepository(ABC):
    @abstractmethod
    def get_by_user(self, user_id: int) -> Fidelidade | None: ...

    @abstractmethod
    def save(self, fidelidade: Fidelidade) -> Fidelidade: ...
