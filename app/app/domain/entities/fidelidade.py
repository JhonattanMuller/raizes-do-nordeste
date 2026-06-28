"""Entidade Fidelidade: saldo de pontos de um usuário.

Regra de negócio: acúmulo e resgate exigem consentimento LGPD do titular.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.core.exceptions import SaldoFidelidadeInsuficienteError


@dataclass
class Fidelidade:
    user_id: int
    pontos: int = 0
    id: int | None = None

    def acumular(self, pontos: int) -> None:
        if pontos < 0:
            raise ValueError("Pontos a acumular não podem ser negativos")
        self.pontos += pontos

    def resgatar(self, pontos: int) -> None:
        if pontos <= 0:
            raise ValueError("Pontos a resgatar devem ser positivos")
        if pontos > self.pontos:
            raise SaldoFidelidadeInsuficienteError()
        self.pontos -= pontos
