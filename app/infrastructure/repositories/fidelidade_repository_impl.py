"""Implementação SQLAlchemy do FidelidadeRepository."""
from sqlalchemy.orm import Session

from app.domain.entities.fidelidade import Fidelidade
from app.domain.repositories.fidelidade_repository import FidelidadeRepository
from app.infrastructure import mappers, models


class SQLFidelidadeRepository(FidelidadeRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_user(self, user_id: int) -> Fidelidade | None:
        orm = (
            self.db.query(models.FidelidadeORM)
            .filter(models.FidelidadeORM.user_id == user_id)
            .first()
        )
        return mappers.fidelidade_to_domain(orm) if orm else None

    def save(self, fidelidade: Fidelidade) -> Fidelidade:
        if fidelidade.id:
            orm = self.db.get(models.FidelidadeORM, fidelidade.id)
            orm.pontos = fidelidade.pontos
        else:
            orm = (
                self.db.query(models.FidelidadeORM)
                .filter(models.FidelidadeORM.user_id == fidelidade.user_id)
                .first()
            )
            if orm:
                orm.pontos = fidelidade.pontos
            else:
                orm = models.FidelidadeORM(
                    user_id=fidelidade.user_id, pontos=fidelidade.pontos
                )
                self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return mappers.fidelidade_to_domain(orm)