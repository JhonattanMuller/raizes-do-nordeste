"""Schemas (DTOs) de autenticação."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.enums import Role


class RegisterRequest(BaseModel):
    nome: str = Field(..., min_length=1, examples=["Maria Silva"])
    email: EmailStr = Field(..., examples=["maria@email.com"])
    senha: str = Field(..., min_length=3, examples=["senha123"])
    consentimento_lgpd: bool = Field(
        ..., alias="consentimentoLgpd", description="Obrigatório true (LGPD).",
        examples=[True],
    )
    role: Role = Field(default=Role.CLIENTE, examples=[Role.CLIENTE])

    model_config = ConfigDict(populate_by_name=True)


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["maria@email.com"])
    senha: str = Field(..., examples=["senha123"])


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    role: str
    consentimento_lgpd: bool = Field(serialization_alias="consentimentoLgpd")

    model_config = ConfigDict(populate_by_name=True)


class TokenResponse(BaseModel):
    access_token: str = Field(serialization_alias="accessToken")
    token_type: str = Field(default="Bearer", serialization_alias="tokenType")
    expires_in: int = Field(serialization_alias="expiresIn")
    user: UsuarioResponse

    model_config = ConfigDict(populate_by_name=True)