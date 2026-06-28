"""Implementação SQLAlchemy do PedidoRepository."""
from sqlalchemy.orm import Session

from app.domain.entities.pedido import Pedido
from app.domain.enums import CanalPedido, StatusPedido
from app.domain.repositories.pedido_repository import PedidoRepository
from app.infrastructure import mappers, models


class SQLPedidoRepository(PedidoRepository):
    def __init__(self, db: Session):
        self.db = db

    def add(self, pedido: Pedido) -> Pedido:
        orm = models.PedidoORM(
            user_id=pedido.user_id,
            unidade_id=pedido.unidade_id,
            canal_pedido=pedido.canal_pedido.value,
            status=pedido.status.value,
        )
        for item in pedido.itens:
            orm.itens.append(
                models.ItemPedidoORM(
                    produto_id=item.produto_id,
                    quantidade=item.quantidade,
                    preco_unitario_cents=item.preco_unitario.cents,
                )
            )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return mappers.pedido_to_domain(orm)

    def get_by_id(self, pedido_id: int) -> Pedido | None:
        orm = self.db.get(models.PedidoORM, pedido_id)
        return mappers.pedido_to_domain(orm) if orm else None

    def update(self, pedido: Pedido) -> Pedido:
        orm = self.db.get(models.PedidoORM, pedido.id)
        orm.status = pedido.status.value
        self.db.commit()
        self.db.refresh(orm)
        return mappers.pedido_to_domain(orm)

    def list(
        self,
        canal: CanalPedido | None = None,
        status: StatusPedido | None = None,
        unidade_id: int | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> list[Pedido]:
        query = self.db.query(models.PedidoORM)
        if canal:
            query = query.filter(models.PedidoORM.canal_pedido == canal.value)
        if status:
            query = query.filter(models.PedidoORM.status == status.value)
        if unidade_id:
            query = query.filter(models.PedidoORM.unidade_id == unidade_id)
        rows = (
            query.order_by(models.PedidoORM.id).offset(offset).limit(limit).all()
        )
        return [mappers.pedido_to_domain(o) for o in rows]
