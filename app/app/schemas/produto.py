"""Schemas (DTOs) de produto e estoque."""
from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import TipoMovimentoEstoque


class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1, examples=["Acarajé"])
    preco: float = Field(..., gt=0, examples=[12.0])


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    preco: float
    ativo: bool


class EstoqueItemResponse(BaseModel):
    unidade_id: int = Field(serialization_alias="unidadeId")
    produto_id: int = Field(serialization_alias="produtoId")
    nome_produto: str | None = Field(default=None, serialization_alias="nomeProduto")
    quantidade: int

    model_config = ConfigDict(populate_by_name=True)


class MovimentoEstoqueRequest(BaseModel):
    produto_id: int = Field(..., alias="produtoId", examples=[1])
    tipo: TipoMovimentoEstoque = Field(..., examples=[TipoMovimentoEstoque.ENTRADA])
    quantidade: int = Field(..., gt=0, examples=[10])

    model_config = ConfigDict(populate_by_name=True)
