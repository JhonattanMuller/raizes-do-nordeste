"""Implementação SQLAlchemy do ProdutoRepository."""
from sqlalchemy.orm import Session

from app.domain.entities.produto import Produto
from app.domain.repositories.produto_repository import ProdutoRepository
from app.infrastructure import mappers, models


class SQLProdutoRepository(ProdutoRepository):
    def __init__(self, db: Session):
        self.db = db

    def add(self, produto: Produto) -> Produto:
        orm = models.ProdutoORM(
            nome=produto.nome, preco_cents=produto.preco.cents, ativo=produto.ativo
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return mappers.produto_to_domain(orm)

    def get_by_id(self, produto_id: int) -> Produto | None:
        orm = self.db.get(models.ProdutoORM, produto_id)
        return mappers.produto_to_domain(orm) if orm else None

    def list(self, offset: int = 0, limit: int = 10) -> list[Produto]:
        rows = (
            self.db.query(models.ProdutoORM)
            .order_by(models.ProdutoORM.id)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [mappers.produto_to_domain(o) for o in rows]

    def update(self, produto: Produto) -> Produto:
        orm = self.db.get(models.ProdutoORM, produto.id)
        orm.nome = produto.nome
        orm.preco_cents = produto.preco.cents
        orm.ativo = produto.ativo
        self.db.commit()
        self.db.refresh(orm)
        return mappers.produto_to_domain(orm)