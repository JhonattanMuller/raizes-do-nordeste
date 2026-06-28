"""Schemas (DTOs) de fidelidade."""
from pydantic import BaseModel, Field


class FidelidadeResponse(BaseModel):
    user_id: int = Field(serialization_alias="userId")
    pontos: int

    model_config = {"populate_by_name": True}


class ResgateRequest(BaseModel):
    pontos: int = Field(..., gt=0, examples=[50])
