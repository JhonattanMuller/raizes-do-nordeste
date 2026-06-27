"""Caso de uso: unidades da rede e cardápio por unidade."""
from app.core.exceptions import UnidadeNaoEncontradaError
from app.domain.entities.estoque_item import EstoqueItem
from app.domain.entities.unidade import Unidade
from app.domain.repositories.estoque_repository import EstoqueRepository
from app.domain.repositories.unidade_repository import UnidadeRepository


class UnidadeService:
    def __init__(self, unidades: UnidadeRepository, estoque: EstoqueRepository):
        self.unidades = unidades
        self.estoque = estoque

    def criar(self, nome: str, cidade: str) -> Unidade:
        return self.unidades.add(Unidade(id=None, nome=nome, cidade=cidade))

    def listar(self, offset: int = 0, limit: int = 10) -> list[Unidade]:
        return self.unidades.list(offset=offset, limit=limit)

    def obter(self, unidade_id: int) -> Unidade:
        unidade = self.unidades.get_by_id(unidade_id)
        if not unidade:
            raise UnidadeNaoEncontradaError()
        return unidade

    def cardapio(self, unidade_id: int) -> list[EstoqueItem]:
        """Itens disponíveis na unidade (com estoque cadastrado)."""
        self.obter(unidade_id)  # valida existência
        return self.estoque.list_por_unidade(unidade_id)
