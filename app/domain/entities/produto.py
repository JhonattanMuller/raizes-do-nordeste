"""Entidade Produto (item de cardápio / catálogo da rede).

O estoque NÃO fica no produto: cada unidade tem seu próprio estoque
(ver EstoqueItem), pois a rede é multiunidade.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.domain.value_objects.money import Money


@dataclass
class Produto:
    id: int | None
    nome: str
    preco: Money
    ativo: bool = True