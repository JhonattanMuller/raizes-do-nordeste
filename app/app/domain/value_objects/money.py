"""Value Object Money: representa valores monetários de forma imutável e segura.

Trabalha internamente em centavos (int) para evitar erros de ponto flutuante.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    cents: int

    def __post_init__(self):
        if not isinstance(self.cents, int):
            raise ValueError("Money.cents deve ser inteiro (centavos)")
        if self.cents < 0:
            raise ValueError("Money não pode ser negativo")

    @classmethod
    def from_reais(cls, valor: float) -> "Money":
        return cls(int(round(valor * 100)))

    @property
    def reais(self) -> float:
        return self.cents / 100

    def __add__(self, other: "Money") -> "Money":
        return Money(self.cents + other.cents)

    def __mul__(self, qty: int) -> "Money":
        return Money(self.cents * qty)

    def __str__(self) -> str:
        return f"R$ {self.reais:.2f}"
