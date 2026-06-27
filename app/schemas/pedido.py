"""Schemas (DTOs) de pedido."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import CanalPedido, StatusPedido


class ItemPedidoInput(BaseModel):
    produto_id: int = Field(..., alias="produtoId", examples=[1])
    quantidade: int = Field(..., gt=0, examples=[2])

    model_config = ConfigDict(populate_by_name=True)


class PedidoCreate(BaseModel):
    canal_pedido: CanalPedido = Field(
        ..., alias="canalPedido", examples=[CanalPedido.TOTEM]
    )
    unidade_id: int = Field(..., alias="unidadeId", examples=[1])
    itens: list[ItemPedidoInput] = Field(..., min_length=1)
    forma_pagamento: str | None = Field(
        default="MOCK", alias="formaPagamento", examples=["MOCK"]
    )

    model_config = ConfigDict(populate_by_name=True)


class ItemPedidoResponse(BaseModel):
    produto_id: int = Field(serialization_alias="produtoId")
    nome_produto: str | None = Field(default=None, serialization_alias="nomeProduto")
    quantidade: int
    preco_unitario: float = Field(serialization_alias="precoUnitario")
    subtotal: float

    model_config = ConfigDict(populate_by_name=True)


class PedidoResponse(BaseModel):
    id: int = Field(serialization_alias="pedidoId")
    user_id: int = Field(serialization_alias="clienteId")
    unidade_id: int = Field(serialization_alias="unidadeId")
    canal_pedido: CanalPedido = Field(serialization_alias="canalPedido")
    status: StatusPedido
    total: float
    itens: list[ItemPedidoResponse]
    created_at: datetime | None = Field(
        default=None, serialization_alias="createdAt"
    )

    model_config = ConfigDict(populate_by_name=True)


class AtualizarStatusRequest(BaseModel):
    status: StatusPedido = Field(..., examples=[StatusPedido.EM_PREPARO])
