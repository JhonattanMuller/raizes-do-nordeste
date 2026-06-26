"""Entidade Usuario (aggregate root do contexto de identidade)."""
from __future__ import annotations

from dataclasses import dataclass

from app.core.exceptions import ConsentimentoLGPDObrigatorioError
from app.domain.enums import Role
from app.domain.value_objects.email import Email


@dataclass
class Usuario:
    id: int | None
    nome: str
    email: Email
    senha_hash: str
    role: Role = Role.CLIENTE
    consentimento_lgpd: bool = False

    @classmethod
    def registrar(
        cls,
        nome: str,
        email: Email,
        senha_hash: str,
        consentimento_lgpd: bool,
        role: Role = Role.CLIENTE,
    ) -> "Usuario":
        # Regra LGPD: sem consentimento não há cadastro com uso de dados/fidelidade.
        if not consentimento_lgpd:
            raise ConsentimentoLGPDObrigatorioError()
        return cls(
            id=None,
            nome=nome.strip(),
            email=email,
            senha_hash=senha_hash,
            role=role,
            consentimento_lgpd=consentimento_lgpd,
        )