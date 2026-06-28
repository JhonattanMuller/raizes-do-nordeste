"""Entidade ItemPedido (parte do agregado Pedido)."""
from __future__ import annotations

from dataclasses import dataclass

from app.domain.value_objects.money import Money


@dataclass
class ItemPedido:
    produto_id: int
    quantidade: int
    preco_unitario: Money
    id: int | None = None
    nome_produto: str | None = None

    def __post_init__(self):
        if self.quantidade <= 0:
            raise ValueError("Quantidade do item deve ser maior que zero")

    @property
    def subtotal(self) -> Money:
        return self.preco_unitario * self.quantidade
