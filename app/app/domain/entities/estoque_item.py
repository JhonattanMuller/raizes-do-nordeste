"""Entidade EstoqueItem: estoque de um produto EM UMA unidade.

Concentra a invariante de não permitir estoque negativo.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.core.exceptions import EstoqueInsuficienteError


@dataclass
class EstoqueItem:
    unidade_id: int
    produto_id: int
    quantidade: int
    id: int | None = None
    nome_produto: str | None = None

    def tem(self, quantidade: int) -> bool:
        return self.quantidade >= quantidade

    def validar(self, quantidade: int) -> None:
        if not self.tem(quantidade):
            raise EstoqueInsuficienteError(
                details=[
                    {
                        "field": f"produto_id:{self.produto_id}",
                        "issue": f"Disponível: {self.quantidade}",
                    }
                ]
            )

    def saida(self, quantidade: int) -> None:
        """Baixa de estoque (saída)."""
        self.validar(quantidade)
        self.quantidade -= quantidade

    def entrada(self, quantidade: int) -> None:
        """Entrada/reposição de estoque."""
        if quantidade <= 0:
            raise ValueError("Quantidade de entrada deve ser positiva")
        self.quantidade += quantidade
