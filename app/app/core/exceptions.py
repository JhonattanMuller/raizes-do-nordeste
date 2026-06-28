"""Exceções de domínio/aplicação e padronização das respostas de erro.

Formato do erro (conforme o roteiro da atividade):
    {
      "error": "ESTOQUE_INSUFICIENTE",
      "message": "Não há quantidade suficiente para um ou mais itens.",
      "details": [{"field": "itens[0].quantidade", "issue": "Disponível: 1"}],
      "timestamp": "2026-06-23T12:00:00Z",
      "path": "/pedidos"
    }
"""
from datetime import datetime, timezone

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _body(error: str, message: str, details: list, path: str) -> dict:
    return {
        "error": error,
        "message": message,
        "details": details or [],
        "timestamp": _now_iso(),
        "path": path,
    }


class DomainError(Exception):
    """Erro de regra de negócio. `error` é o código; `message` é legível."""

    error: str = "DOMAIN_ERROR"
    message: str = "Erro de domínio."
    status_code: int = 400

    def __init__(
        self,
        message: str | None = None,
        details: list | None = None,
        error: str | None = None,
        status_code: int | None = None,
    ):
        if error:
            self.error = error
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        self.details = details or []
        super().__init__(self.message)


# ---------- 401 / 403 ----------
class CredenciaisInvalidasError(DomainError):
    error = "CREDENCIAIS_INVALIDAS"
    message = "E-mail ou senha inválidos."
    status_code = 401


class NaoAutenticadoError(DomainError):
    error = "NAO_AUTENTICADO"
    message = "Autenticação necessária (token ausente ou inválido)."
    status_code = 401


class SemPermissaoError(DomainError):
    error = "SEM_PERMISSAO"
    message = "Seu perfil não tem permissão para esta ação."
    status_code = 403


# ---------- 404 ----------
class ProdutoNaoEncontradoError(DomainError):
    error = "PRODUTO_NAO_ENCONTRADO"
    message = "Produto não encontrado."
    status_code = 404


class UnidadeNaoEncontradaError(DomainError):
    error = "UNIDADE_NAO_ENCONTRADA"
    message = "Unidade não encontrada."
    status_code = 404


class PedidoNaoEncontradoError(DomainError):
    error = "PEDIDO_NAO_ENCONTRADO"
    message = "Pedido não encontrado."
    status_code = 404


# ---------- 409 ----------
class EstoqueInsuficienteError(DomainError):
    error = "ESTOQUE_INSUFICIENTE"
    message = "Não há quantidade suficiente para um ou mais itens."
    status_code = 409


class PagamentoJaProcessadoError(DomainError):
    error = "PAGAMENTO_JA_PROCESSADO"
    message = "Este pedido já possui um pagamento registrado."
    status_code = 409


class EmailJaCadastradoError(DomainError):
    error = "EMAIL_JA_CADASTRADO"
    message = "Já existe um usuário com este e-mail."
    status_code = 409


class SaldoFidelidadeInsuficienteError(DomainError):
    error = "SALDO_FIDELIDADE_INSUFICIENTE"
    message = "Saldo de pontos insuficiente para o resgate."
    status_code = 409


# ---------- 422 ----------
class TransicaoStatusInvalidaError(DomainError):
    error = "TRANSICAO_STATUS_INVALIDA"
    message = "Transição de status não permitida."
    status_code = 422


class ConsentimentoLGPDObrigatorioError(DomainError):
    error = "CONSENTIMENTO_LGPD_OBRIGATORIO"
    message = "O consentimento LGPD é obrigatório."
    status_code = 422


class PedidoSemItensError(DomainError):
    error = "PEDIDO_SEM_ITENS"
    message = "O pedido deve conter ao menos um item."
    status_code = 422


def register_exception_handlers(app):
    """Registra os handlers que padronizam o corpo de erro da API."""

    @app.exception_handler(DomainError)
    async def _domain(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(exc.error, exc.message, exc.details, request.url.path),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError):
        details = [
            {
                "field": ".".join(str(p) for p in e.get("loc", []) if p != "body"),
                "issue": e.get("msg", "inválido"),
            }
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_body(
                "VALIDACAO", "Requisição inválida.", details, request.url.path
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException):
        mapa = {401: "NAO_AUTENTICADO", 403: "SEM_PERMISSAO", 404: "NAO_ENCONTRADO"}
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(
                mapa.get(exc.status_code, "ERRO"),
                str(exc.detail),
                [],
                request.url.path,
            ),
        )
