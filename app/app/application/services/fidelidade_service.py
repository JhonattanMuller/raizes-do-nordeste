"""Caso de uso: programa de fidelidade (pontos e resgate, com consentimento LGPD)."""
from app.core.exceptions import ConsentimentoLGPDObrigatorioError
from app.domain.entities.fidelidade import Fidelidade
from app.domain.repositories.fidelidade_repository import FidelidadeRepository
from app.domain.repositories.usuario_repository import UsuarioRepository
from app.domain.value_objects.money import Money


class FidelidadeService:
    def __init__(
        self, fidelidade: FidelidadeRepository, usuarios: UsuarioRepository
    ):
        self.fidelidade = fidelidade
        self.usuarios = usuarios

    def _saldo(self, user_id: int) -> Fidelidade:
        return self.fidelidade.get_by_user(user_id) or Fidelidade(
            user_id=user_id, pontos=0
        )

    def saldo(self, user_id: int) -> Fidelidade:
        return self._saldo(user_id)

    def acumular_por_compra(self, user_id: int, total: Money) -> Fidelidade:
        """Acumula pontos somente se o usuário consentiu (LGPD)."""
        usuario = self.usuarios.get_by_id(user_id)
        if not usuario or not usuario.consentimento_lgpd:
            return self._saldo(user_id)  # sem consentimento: não acumula
        pontos = int(total.reais)  # 1 ponto por R$1
        f = self._saldo(user_id)
        f.acumular(pontos)
        return self.fidelidade.save(f)

    def resgatar(self, user_id: int, pontos: int) -> Fidelidade:
        usuario = self.usuarios.get_by_id(user_id)
        if not usuario or not usuario.consentimento_lgpd:
            raise ConsentimentoLGPDObrigatorioError(
                message="Resgate de fidelidade requer consentimento LGPD."
            )
        f = self._saldo(user_id)
        f.resgatar(pontos)  # valida saldo
        return self.fidelidade.save(f)
