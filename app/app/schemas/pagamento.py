"""Schemas (DTOs) de pagamento."""
from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import StatusPagamento


class PagamentoRequest(BaseModel):
    # Permite forçar o resultado em demos/testes; None = aleatório (mock).
    aprovar: bool | None = Field(default=None, examples=[True])


class PagamentoResponse(BaseModel):
    id: int = Field(serialization_alias="pagamentoId")
    pedido_id: int = Field(serialization_alias="pedidoId")
    valor: float
    status: StatusPagamento

    model_config = ConfigDict(populate_by_name=True)
