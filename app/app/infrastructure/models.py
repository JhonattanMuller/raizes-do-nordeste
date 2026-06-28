"""Modelos ORM (camada de persistência). Não contêm regra de negócio."""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class UsuarioORM(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="CLIENTE")
    consentimento_lgpd = Column(Boolean, nullable=False, default=False)

    pedidos = relationship("PedidoORM", back_populates="usuario")


class UnidadeORM(Base):
    __tablename__ = "unidades"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cidade = Column(String, nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)


class ProdutoORM(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco_cents = Column(Integer, nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)


class EstoqueUnidadeORM(Base):
    """Estoque de um produto em uma unidade específica (cardápio por unidade)."""

    __tablename__ = "estoque_unidade"
    __table_args__ = (
        UniqueConstraint("unidade_id", "produto_id", name="uq_estoque_unidade_produto"),
    )

    id = Column(Integer, primary_key=True, index=True)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False, default=0)

    produto = relationship("ProdutoORM")
    unidade = relationship("UnidadeORM")


class PedidoORM(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    unidade_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)
    canal_pedido = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    usuario = relationship("UsuarioORM", back_populates="pedidos")
    itens = relationship(
        "ItemPedidoORM", back_populates="pedido", cascade="all, delete-orphan"
    )
    pagamento = relationship("PagamentoORM", back_populates="pedido", uselist=False)


class ItemPedidoORM(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario_cents = Column(Integer, nullable=False)

    pedido = relationship("PedidoORM", back_populates="itens")
    produto = relationship("ProdutoORM")


class PagamentoORM(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), unique=True, nullable=False)
    valor_cents = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="PENDENTE")

    pedido = relationship("PedidoORM", back_populates="pagamento")


class FidelidadeORM(Base):
    __tablename__ = "fidelidade"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    pontos = Column(Integer, nullable=False, default=0)


class AuditoriaORM(Base):
    """Registro de ações sensíveis (LGPD / rastreabilidade)."""

    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True)
    acao = Column(String, nullable=False)
    entidade = Column(String, nullable=False)
    entidade_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)
    detalhe = Column(String, nullable=True)
    timestamp = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
