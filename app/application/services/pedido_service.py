"""Caso de uso: criação, consulta e ciclo de vida do pedido (coração do sistema)."""
from app.application.services.estoque_service import EstoqueService
from app.core.exceptions import (
    PedidoNaoEncontradoError,
    ProdutoNaoEncontradoError,
    UnidadeNaoEncontradaError,
)
from app.domain.entities.item_pedido import ItemPedido
from app.domain.entities.pedido import Pedido
from app.domain.enums import CanalPedido, StatusPedido
from app.domain.repositories.auditoria_repository import AuditoriaRepository
from app.domain.repositories.pedido_repository import PedidoRepository
from app.domain.repositories.produto_repository import ProdutoRepository
from app.domain.repositories.unidade_repository import UnidadeRepository


class PedidoService:
    def __init__(
        self,
        pedidos: PedidoRepository,
        produtos: ProdutoRepository,
        unidades: UnidadeRepository,
        estoque: EstoqueService,
        auditoria: AuditoriaRepository,
    ):
        self.pedidos = pedidos
        self.produtos = produtos
        self.unidades = unidades
        self.estoque = estoque
        self.auditoria = auditoria

    def criar(
        self, user_id: int, unidade_id: int, canal: CanalPedido, itens_input: list[dict]
    ) -> Pedido:
        if self.unidades.get_by_id(unidade_id) is None:
            raise UnidadeNaoEncontradaError()

        itens: list[ItemPedido] = []
        for raw in itens_input:
            produto = self.produtos.get_by_id(raw["produto_id"])
            if produto is None:
                raise ProdutoNaoEncontradoError()
            itens.append(
                ItemPedido(
                    produto_id=produto.id,
                    quantidade=raw["quantidade"],
                    preco_unitario=produto.preco,
                    nome_produto=produto.nome,
                )
            )

        # Regra: não permite pedido sem estoque na unidade (valida antes de persistir).
        self.estoque.validar_disponibilidade(unidade_id, itens)

        pedido = Pedido.criar(
            user_id=user_id, unidade_id=unidade_id, canal=canal, itens=itens
        )
        pedido = self.pedidos.add(pedido)
        self.auditoria.registrar(
            "CRIAR_PEDIDO", "Pedido", pedido.id, user_id,
            f"unidade={unidade_id} canal={canal.value} total={pedido.total}",
        )
        return pedido

    def obter(self, pedido_id: int) -> Pedido:
        pedido = self.pedidos.get_by_id(pedido_id)
        if not pedido:
            raise PedidoNaoEncontradoError()
        return pedido

    def listar(
        self,
        canal: CanalPedido | None = None,
        status: StatusPedido | None = None,
        unidade_id: int | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[Pedido]:
        return self.pedidos.list(
            canal=canal, status=status, unidade_id=unidade_id,
            offset=offset, limit=limit,
        )

    def atualizar_status(
        self, pedido_id: int, novo_status: StatusPedido, user_id: int | None = None
    ) -> Pedido:
        pedido = self.obter(pedido_id)
        anterior = pedido.status
        pedido.atualizar_status(novo_status)  # valida a máquina de estados
        pedido = self.pedidos.update(pedido)
        self.auditoria.registrar(
            "ATUALIZAR_STATUS", "Pedido", pedido.id, user_id,
            f"{anterior.value} -> {novo_status.value}",
        )
        return pedido

    def cancelar(self, pedido_id: int, user_id: int | None = None) -> Pedido:
        pedido = self.obter(pedido_id)
        repor = pedido.estoque_foi_baixado  # se já pago, devolve ao estoque
        pedido.cancelar()
        pedido = self.pedidos.update(pedido)
        if repor:
            self.estoque.repor_itens(pedido.unidade_id, pedido.itens)
        self.auditoria.registrar(
            "CANCELAR_PEDIDO", "Pedido", pedido.id, user_id,
            f"estoque_reposto={repor}",
        )
        return pedido
