"""Caso de uso: gestão de estoque por unidade (entrada/saída/consulta)."""
from app.core.exceptions import (
    ProdutoNaoEncontradoError,
    UnidadeNaoEncontradaError,
)
from app.domain.entities.estoque_item import EstoqueItem
from app.domain.repositories.estoque_repository import EstoqueRepository
from app.domain.repositories.produto_repository import ProdutoRepository
from app.domain.repositories.unidade_repository import UnidadeRepository


class EstoqueService:
    def __init__(
        self,
        estoque: EstoqueRepository,
        produtos: ProdutoRepository,
        unidades: UnidadeRepository,
    ):
        self.estoque = estoque
        self.produtos = produtos
        self.unidades = unidades

    def _obter_item(self, unidade_id: int, produto_id: int) -> EstoqueItem:
        item = self.estoque.get(unidade_id, produto_id)
        if item is None:
            # Produto sem estoque cadastrado na unidade = indisponível (0).
            if self.produtos.get_by_id(produto_id) is None:
                raise ProdutoNaoEncontradoError()
            return EstoqueItem(
                unidade_id=unidade_id, produto_id=produto_id, quantidade=0
            )
        return item

    def validar_disponibilidade(self, unidade_id: int, itens: list) -> None:
        """Garante estoque na unidade para todos os itens (regra: não vender sem estoque)."""
        for item in itens:
            self._obter_item(unidade_id, item.produto_id).validar(item.quantidade)

    def dar_baixa(self, unidade_id: int, itens: list) -> None:
        """Baixa automática de estoque (saída) na unidade."""
        for item in itens:
            est = self._obter_item(unidade_id, item.produto_id)
            est.saida(item.quantidade)
            self.estoque.update(est)

    def repor_itens(self, unidade_id: int, itens: list) -> None:
        """Repõe o estoque (usado ao cancelar pedido já pago)."""
        for item in itens:
            est = self.estoque.get(unidade_id, item.produto_id)
            if est:
                est.entrada(item.quantidade)
                self.estoque.update(est)

    def movimentar(
        self, unidade_id: int, produto_id: int, tipo: str, quantidade: int
    ) -> EstoqueItem:
        """Entrada/saída manual de estoque na unidade."""
        if self.unidades.get_by_id(unidade_id) is None:
            raise UnidadeNaoEncontradaError()
        if self.produtos.get_by_id(produto_id) is None:
            raise ProdutoNaoEncontradoError()
        item = self.estoque.get(unidade_id, produto_id)
        if item is None:
            item = self.estoque.add(
                EstoqueItem(unidade_id=unidade_id, produto_id=produto_id, quantidade=0)
            )
        if tipo == "ENTRADA":
            item.entrada(quantidade)
        else:
            item.saida(quantidade)
        return self.estoque.update(item)

    def consultar_unidade(self, unidade_id: int) -> list[EstoqueItem]:
        if self.unidades.get_by_id(unidade_id) is None:
            raise UnidadeNaoEncontradaError()
        return self.estoque.list_por_unidade(unidade_id)
