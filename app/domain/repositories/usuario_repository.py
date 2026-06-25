"""Porta (interface) do repositório de Usuario."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.usuario import Usuario


class UsuarioRepository(ABC):
    @abstractmethod
    def add(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    def get_by_email(self, email: str) -> Usuario | None: ...

    @abstractmethod
    def get_by_id(self, usuario_id: int) -> Usuario | None: ...
