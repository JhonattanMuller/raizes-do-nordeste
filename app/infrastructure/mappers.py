"""Mapeadores entre entidades de domínio e modelos ORM (anti-corruption)."""
from app.domain.entities.estoque_item import EstoqueItem
from app.domain.entities.fidelidade import Fidelidade
from app.domain.entities.item_pedido import ItemPedido
from app.domain.entities.pagamento import Pagamento
from app.domain.entities.pedido import Pedido
from app.domain.entities.produto import Produto
from app.domain.entities.unidade import Unidade
from app.domain.entities.usuario import Usuario
from app.domain.enums import (
    CanalPedido,
    Role,
    StatusPagamento,
    StatusPedido,
)
from app.domain.value_objects.email import Email
from app.domain.value_objects.money import Money
from app.infrastructure import models


# ---------- Usuario ----------
def usuario_to_domain(o: models.UsuarioORM) -> Usuario:
    return Usuario(
        id=o.id,
        nome=o.nome,
        email=Email(o.email),
        senha_hash=o.senha_hash,
        role=Role(o.role),
        consentimento_lgpd=o.consentimento_lgpd,
    )


def usuario_to_orm(e: Usuario) -> models.UsuarioORM:
    return models.UsuarioORM(
        id=e.id,
        nome=e.nome,
        email=str(e.email),
        senha_hash=e.senha_hash,
        role=e.role.value,
        consentimento_lgpd=e.consentimento_lgpd,
    )


# ---------- Unidade ----------
def unidade_to_domain(o: models.UnidadeORM) -> Unidade:
    return Unidade(id=o.id, nome=o.nome, cidade=o.cidade, ativo=o.ativo)


# ---------- Produto ----------
def produto_to_domain(o: models.ProdutoORM) -> Produto:
    return Produto(id=o.id, nome=o.nome, preco=Money(o.preco_cents), ativo=o.ativo)


# ---------- EstoqueItem ----------
def estoque_to_domain(o: models.EstoqueUnidadeORM) -> EstoqueItem:
    return EstoqueItem(
        id=o.id,
        unidade_id=o.unidade_id,
        produto_id=o.produto_id,
        quantidade=o.quantidade,
        nome_produto=o.produto.nome if o.produto else None,
    )


# ---------- ItemPedido ----------
def item_to_domain(o: models.ItemPedidoORM) -> ItemPedido:
    return ItemPedido(
        id=o.id,
        produto_id=o.produto_id,
        quantidade=o.quantidade,
        preco_unitario=Money(o.preco_unitario_cents),
        nome_produto=o.produto.nome if o.produto else None,
    )


# ---------- Pedido ----------
def pedido_to_domain(o: models.PedidoORM) -> Pedido:
    return Pedido(
        id=o.id,
        user_id=o.user_id,
        unidade_id=o.unidade_id,
        canal_pedido=CanalPedido(o.canal_pedido),
        status=StatusPedido(o.status),
        itens=[item_to_domain(i) for i in o.itens],
        created_at=o.created_at,
    )


# ---------- Pagamento ----------
def pagamento_to_domain(o: models.PagamentoORM) -> Pagamento:
    return Pagamento(
        id=o.id,
        pedido_id=o.pedido_id,
        valor=Money(o.valor_cents),
        status=StatusPagamento(o.status),
    )


# ---------- Fidelidade ----------
def fidelidade_to_domain(o: models.FidelidadeORM) -> Fidelidade:
    return Fidelidade(id=o.id, user_id=o.user_id, pontos=o.pontos)