"""Implementação SQLAlchemy do UnidadeRepository."""
from sqlalchemy.orm import Session

from app.domain.entities.unidade import Unidade
from app.domain.repositories.unidade_repository import UnidadeRepository
from app.infrastructure import mappers, models


class SQLUnidadeRepository(UnidadeRepository):
    def __init__(self, db: Session):
        self.db = db

    def add(self, unidade: Unidade) -> Unidade:
        orm = models.UnidadeORM(
            nome=unidade.nome, cidade=unidade.cidade, ativo=unidade.ativo
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return mappers.unidade_to_domain(orm)

    def get_by_id(self, unidade_id: int) -> Unidade | None:
        orm = self.db.get(models.UnidadeORM, unidade_id)
        return mappers.unidade_to_domain(orm) if orm else None

    def list(self, offset: int = 0, limit: int = 10) -> list[Unidade]:
        rows = (
            self.db.query(models.UnidadeORM)
            .order_by(models.UnidadeORM.id)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [mappers.unidade_to_domain(o) for o in rows]
