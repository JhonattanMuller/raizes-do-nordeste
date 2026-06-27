"""Implementação SQLAlchemy do UsuarioRepository."""
from sqlalchemy.orm import Session

from app.domain.entities.usuario import Usuario
from app.domain.repositories.usuario_repository import UsuarioRepository
from app.infrastructure import mappers, models


class SQLUsuarioRepository(UsuarioRepository):
    def __init__(self, db: Session):
        self.db = db

    def add(self, usuario: Usuario) -> Usuario:
        orm = mappers.usuario_to_orm(usuario)
        orm.id = None
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return mappers.usuario_to_domain(orm)

    def get_by_email(self, email: str) -> Usuario | None:
        orm = (
            self.db.query(models.UsuarioORM)
            .filter(models.UsuarioORM.email == email.lower())
            .first()
        )
        return mappers.usuario_to_domain(orm) if orm else None

    def get_by_id(self, usuario_id: int) -> Usuario | None:
        orm = self.db.get(models.UsuarioORM, usuario_id)
        return mappers.usuario_to_domain(orm) if orm else None
