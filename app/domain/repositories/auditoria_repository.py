"""Porta (interface) do repositório de Auditoria (logs de ações sensíveis)."""
from __future__ import annotations

from abc import ABC, abstractmethod


class AuditoriaRepository(ABC):
    @abstractmethod
    def registrar(
        self,
        acao: str,
        entidade: str,
        entidade_id: int | None,
        user_id: int | None,
        detalhe: str | None = None,
    ) -> None: ...

    @abstractmethod
    def listar(self, offset: int = 0, limit: int = 50) -> list[dict]: ...
