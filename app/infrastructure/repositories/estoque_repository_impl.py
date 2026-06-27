"""Implementação SQLAlchemy do EstoqueRepository (estoque por unidade)."""
from sqlalchemy.orm import Session

from app.domain.entities.estoque_item import EstoqueItem
from app.domain.repositories.estoque_repository import EstoqueRepository
from app.infrastructure import mappers, models


class SQLEstoqueRepository(EstoqueRepository):
    def __init__(self, db: Session):
        self.db = db

    def add(self, item: EstoqueItem) -> EstoqueItem:
        orm = models.EstoqueUnidadeORM(
            unidade_id=item.unidade_id,
            produto_id=item.produto_id,
            quantidade=item.quantidade,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return mappers.estoque_to_domain(orm)

    def get(self, unidade_id: int, produto_id: int) -> EstoqueItem | None:
        orm = (
            self.db.query(models.EstoqueUnidadeORM)
            .filter(
                models.EstoqueUnidadeORM.unidade_id == unidade_id,
                models.EstoqueUnidadeORM.produto_id == produto_id,
            )
            .first()
        )
        return mappers.estoque_to_domain(orm) if orm else None

    def update(self, item: EstoqueItem) -> EstoqueItem:
        orm = self.db.get(models.EstoqueUnidadeORM, item.id)
        orm.quantidade = item.quantidade
        self.db.commit()
        self.db.refresh(orm)
        return mappers.estoque_to_domain(orm)

    def list_por_unidade(self, unidade_id: int) -> list[EstoqueItem]:
        rows = (
            self.db.query(models.EstoqueUnidadeORM)
            .filter(models.EstoqueUnidadeORM.unidade_id == unidade_id)
            .order_by(models.EstoqueUnidadeORM.produto_id)
            .all()
        )
        return [mappers.estoque_to_domain(o) for o in rows]

