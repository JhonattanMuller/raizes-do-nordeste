"""Schemas (DTOs) de unidade."""
from pydantic import BaseModel, Field


class UnidadeCreate(BaseModel):
    nome: str = Field(..., min_length=1, examples=["Unidade Recife - Boa Viagem"])
    cidade: str = Field(..., min_length=1, examples=["Recife"])


class UnidadeResponse(BaseModel):
    id: int
    nome: str
    cidade: str
    ativo: bool
