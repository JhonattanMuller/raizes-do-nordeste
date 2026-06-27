"""Implementação SQLAlchemy do AuditoriaRepository."""
from sqlalchemy.orm import Session

from app.domain.repositories.auditoria_repository import AuditoriaRepository
from app.infrastructure import models


class SQLAuditoriaRepository(AuditoriaRepository):
    def __init__(self, db: Session):
        self.db = db

    def registrar(
        self,
        acao: str,
        entidade: str,
        entidade_id: int | None,
        user_id: int | None,
        detalhe: str | None = None,
    ) -> None:
        orm = models.AuditoriaORM(
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
            user_id=user_id,
            detalhe=detalhe,
        )
        self.db.add(orm)
        self.db.commit()

    def listar(self, offset: int = 0, limit: int = 50) -> list[dict]:
        rows = (
            self.db.query(models.AuditoriaORM)
            .order_by(models.AuditoriaORM.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "acao": r.acao,
                "entidade": r.entidade,
                "entidade_id": r.entidade_id,
                "user_id": r.user_id,
                "detalhe": r.detalhe,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in rows
        ]
