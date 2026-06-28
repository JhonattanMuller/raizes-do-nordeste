"""Conversão de entidades de domínio -> schemas de resposta da API."""
from app.domain.entities.estoque_item import EstoqueItem
from app.domain.entities.fidelidade import Fidelidade
from app.domain.entities.pagamento import Pagamento
from app.domain.entities.pedido import Pedido
from app.domain.entities.produto import Produto
from app.domain.entities.unidade import Unidade
from app.domain.entities.usuario import Usuario
from app.schemas.auth import UsuarioResponse
from app.schemas.fidelidade import FidelidadeResponse
from app.schemas.pagamento import PagamentoResponse
from app.schemas.pedido import ItemPedidoResponse, PedidoResponse
from app.schemas.produto import EstoqueItemResponse, ProdutoResponse
from app.schemas.unidade import UnidadeResponse


def usuario_out(u: Usuario) -> UsuarioResponse:
    return UsuarioResponse(
        id=u.id, nome=u.nome, email=str(u.email), role=u.role.value,
        consentimento_lgpd=u.consentimento_lgpd,
    )


def produto_out(p: Produto) -> ProdutoResponse:
    return ProdutoResponse(id=p.id, nome=p.nome, preco=p.preco.reais, ativo=p.ativo)


def unidade_out(u: Unidade) -> UnidadeResponse:
    return UnidadeResponse(id=u.id, nome=u.nome, cidade=u.cidade, ativo=u.ativo)


def estoque_out(e: EstoqueItem) -> EstoqueItemResponse:
    return EstoqueItemResponse(
        unidade_id=e.unidade_id, produto_id=e.produto_id,
        nome_produto=e.nome_produto, quantidade=e.quantidade,
    )


def pedido_out(p: Pedido) -> PedidoResponse:
    return PedidoResponse(
        id=p.id, user_id=p.user_id, unidade_id=p.unidade_id,
        canal_pedido=p.canal_pedido, status=p.status, total=p.total.reais,
        created_at=p.created_at,
        itens=[
            ItemPedidoResponse(
                produto_id=i.produto_id, nome_produto=i.nome_produto,
                quantidade=i.quantidade, preco_unitario=i.preco_unitario.reais,
                subtotal=i.subtotal.reais,
            )
            for i in p.itens
        ],
    )


def pagamento_out(p: Pagamento) -> PagamentoResponse:
    return PagamentoResponse(
        id=p.id, pedido_id=p.pedido_id, valor=p.valor.reais, status=p.status
    )


def fidelidade_out(f: Fidelidade) -> FidelidadeResponse:
    return FidelidadeResponse(user_id=f.user_id, pontos=f.pontos)
