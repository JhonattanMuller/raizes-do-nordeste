"""Entidade Pagamento (mock de gateway)."""
from __future__ import annotations

import random
from dataclasses import dataclass

from app.domain.enums import StatusPagamento
from app.domain.value_objects.money import Money


@dataclass
class Pagamento:
    id: int | None
    pedido_id: int
    valor: Money
    status: StatusPagamento = StatusPagamento.PENDENTE

    @classmethod
    def processar_mock(
        cls, pedido_id: int, valor: Money, aprovar: bool | None = None
    ) -> "Pagamento":
        """Simula um gateway. `aprovar` força o resultado (útil em testes);
        quando None, aprova ~85% das vezes."""
        if aprovar is None:
            aprovar = random.random() < 0.85
        status = StatusPagamento.APROVADO if aprovar else StatusPagamento.RECUSADO
        return cls(id=None, pedido_id=pedido_id, valor=valor, status=status)

    @property
    def aprovado(self) -> bool:
        return self.status == StatusPagamento.APROVADO
