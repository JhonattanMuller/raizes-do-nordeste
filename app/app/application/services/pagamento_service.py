"""Caso de uso: pagamento mock + efeitos do fluxo principal.

Fluxo: valida pedido -> pagamento mock -> se aprovado: marca PAGO,
baixa estoque da unidade e acumula pontos de fidelidade.
"""
from app.application.services.estoque_service import EstoqueService
from app.application.services.fidelidade_service import FidelidadeService
from app.core.exceptions import (
    PagamentoJaProcessadoError,
    PedidoNaoEncontradoError,
)
from app.domain.entities.pagamento import Pagamento
from app.domain.repositories.auditoria_repository import AuditoriaRepository
from app.domain.repositories.pagamento_repository import PagamentoRepository
from app.domain.repositories.pedido_repository import PedidoRepository


class PagamentoService:
    def __init__(
        self,
        pagamentos: PagamentoRepository,
        pedidos: PedidoRepository,
        estoque: EstoqueService,
        fidelidade: FidelidadeService,
        auditoria: AuditoriaRepository,
    ):
        self.pagamentos = pagamentos
        self.pedidos = pedidos
        self.estoque = estoque
        self.fidelidade = fidelidade
        self.auditoria = auditoria

    def processar(self, pedido_id: int, aprovar: bool | None = None) -> Pagamento:
        pedido = self.pedidos.get_by_id(pedido_id)
        if not pedido:
            raise PedidoNaoEncontradoError()
        if self.pagamentos.get_by_pedido_id(pedido_id):
            raise PagamentoJaProcessadoError()

        pagamento = Pagamento.processar_mock(
            pedido_id=pedido_id, valor=pedido.total, aprovar=aprovar
        )
        pagamento = self.pagamentos.add(pagamento)

        if pagamento.aprovado:
            pedido.marcar_pago()
            self.pedidos.update(pedido)
            self.estoque.dar_baixa(pedido.unidade_id, pedido.itens)
            # Fidelidade: 1 ponto por real gasto (com consentimento do titular).
            self.fidelidade.acumular_por_compra(pedido.user_id, pedido.total)

        self.auditoria.registrar(
            "PAGAMENTO", "Pedido", pedido_id, pedido.user_id,
            f"status={pagamento.status.value} valor={pagamento.valor}",
        )
        return pagamento
