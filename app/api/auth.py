"""Rotas de autenticação."""
from fastapi import APIRouter, Depends, status

from app.api.presenters import usuario_out
from app.application.services.auth_service import AuthService
from app.core.config import settings
from app.core.deps import get_auth_service
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UsuarioResponse,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register", response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED, summary="Registrar usuário",
)
def register(payload: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    usuario = service.registrar(
        nome=payload.nome, email=payload.email, senha=payload.senha,
        consentimento_lgpd=payload.consentimento_lgpd, role=payload.role,
    )
    return usuario_out(usuario)


@router.post("/login", response_model=TokenResponse, summary="Login (JWT)")
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)):
    token, usuario = service.login(payload.email, payload.senha)
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=usuario_out(usuario),
    )
