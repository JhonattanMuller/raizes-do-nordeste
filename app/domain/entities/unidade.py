"""Entidade Unidade (loja/franquia da rede)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Unidade:
    id: int | None
    nome: str
    cidade: str
    ativo: bool = True