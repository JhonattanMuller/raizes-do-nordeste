"""Caso de uso: registro e autenticação de usuários."""
from app.core.exceptions import (
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.domain.entities.usuario import Usuario
from app.domain.enums import Role
from app.domain.repositories.usuario_repository import UsuarioRepository
from app.domain.value_objects.email import Email


class AuthService:
    def __init__(self, usuarios: UsuarioRepository):
        self.usuarios = usuarios

    def registrar(
        self,
        nome: str,
        email: str,
        senha: str,
        consentimento_lgpd: bool,
        role: Role = Role.CLIENTE,
    ) -> Usuario:
        email_vo = Email(email)
        if self.usuarios.get_by_email(str(email_vo)):
            raise EmailJaCadastradoError()
        usuario = Usuario.registrar(
            nome=nome,
            email=email_vo,
            senha_hash=hash_password(senha),
            consentimento_lgpd=consentimento_lgpd,
            role=role,
        )
        return self.usuarios.add(usuario)

    def login(self, email: str, senha: str) -> tuple[str, Usuario]:
        usuario = self.usuarios.get_by_email(email.lower())
        if not usuario or not verify_password(senha, usuario.senha_hash):
            raise CredenciaisInvalidasError()
        token = create_access_token(
            {"sub": str(usuario.email), "uid": usuario.id, "role": usuario.role.value}
        )
        return token, usuario
