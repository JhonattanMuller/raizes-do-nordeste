"""Caso de uso: catálogo de produtos (cardápio base da rede)."""
from app.core.exceptions import ProdutoNaoEncontradoError
from app.domain.entities.produto import Produto
from app.domain.repositories.produto_repository import ProdutoRepository
from app.domain.value_objects.money import Money


class ProdutoService:
    def __init__(self, produtos: ProdutoRepository):
        self.produtos = produtos

    def criar(self, nome: str, preco: float) -> Produto:
        return self.produtos.add(
            Produto(id=None, nome=nome, preco=Money.from_reais(preco))
        )

    def listar(self, offset: int = 0, limit: int = 10) -> list[Produto]:
        return self.produtos.list(offset=offset, limit=limit)

    def obter(self, produto_id: int) -> Produto:
        produto = self.produtos.get_by_id(produto_id)
        if not produto:
            raise ProdutoNaoEncontradoError()
        return produto
