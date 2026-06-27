"""Implementação SQLAlchemy do PagamentoRepository."""
from sqlalchemy.orm import Session

from app.domain.entities.pagamento import Pagamento
from app.domain.repositories.pagamento_repository import PagamentoRepository
from app.infrastructure import mappers, models


class SQLPagamentoRepository(PagamentoRepository):
    def __init__(self, db: Session):
        self.db = db

    def add(self, pagamento: Pagamento) -> Pagamento:
        orm = models.PagamentoORM(
            pedido_id=pagamento.pedido_id,
            valor_cents=pagamento.valor.cents,
            status=pagamento.status.value,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return mappers.pagamento_to_domain(orm)

    def get_by_pedido_id(self, pedido_id: int) -> Pagamento | None:
        orm = (
            self.db.query(models.PagamentoORM)
            .filter(models.PagamentoORM.pedido_id == pedido_id)
            .first()
        )
        return mappers.pagamento_to_domain(orm) if orm else None
