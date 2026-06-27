"""Popula o banco com dados de exemplo (unidades, produtos, estoque, admin)."""
from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.domain.entities.estoque_item import EstoqueItem
from app.domain.entities.produto import Produto
from app.domain.entities.unidade import Unidade
from app.domain.enums import Role
from app.domain.value_objects.money import Money
from app.infrastructure import models
from app.infrastructure.repositories.estoque_repository_impl import (
    SQLEstoqueRepository,
)
from app.infrastructure.repositories.produto_repository_impl import (
    SQLProdutoRepository,
)
from app.infrastructure.repositories.unidade_repository_impl import (
    SQLUnidadeRepository,
)
from app.infrastructure.repositories.usuario_repository_impl import (
    SQLUsuarioRepository,
)

UNIDADES_SEED = [
    {"nome": "Unidade Recife - Boa Viagem", "cidade": "Recife"},
    {"nome": "Unidade Fortaleza - Centro", "cidade": "Fortaleza"},
]

PRODUTOS_SEED = [
    {"nome": "Baião de Dois", "preco": 28.90},
    {"nome": "Carne de Sol com Macaxeira", "preco": 34.50},
    {"nome": "Acarajé", "preco": 12.00},
    {"nome": "Tapioca de Queijo Coalho", "preco": 15.00},
    {"nome": "Caldo de Sururu", "preco": 22.00},
    {"nome": "Suco de Cajá", "preco": 9.50},
]


def run_seed(db: Session) -> None:
    produtos_repo = SQLProdutoRepository(db)
    unidades_repo = SQLUnidadeRepository(db)
    estoque_repo = SQLEstoqueRepository(db)

    if db.query(models.UnidadeORM).count() == 0:
        for u in UNIDADES_SEED:
            unidades_repo.add(Unidade(id=None, nome=u["nome"], cidade=u["cidade"]))

    if db.query(models.ProdutoORM).count() == 0:
        for p in PRODUTOS_SEED:
            produtos_repo.add(
                Produto(id=None, nome=p["nome"], preco=Money.from_reais(p["preco"]))
            )

    # Estoque inicial: todos os produtos em todas as unidades.
    if db.query(models.EstoqueUnidadeORM).count() == 0:
        for u in unidades_repo.list(0, 100):
            for p in produtos_repo.list(0, 100):
                estoque_repo.add(
                    EstoqueItem(unidade_id=u.id, produto_id=p.id, quantidade=50)
                )

    auth = AuthService(SQLUsuarioRepository(db))
    seed_users = [
        ("Administrador", "admin@raizes.com", "admin123", Role.ADMIN),
        ("Gerente", "gerente@raizes.com", "gerente123", Role.GERENTE),
        ("Atendente", "atendente@raizes.com", "atend123", Role.ATENDENTE),
    ]
    for nome, email, senha, role in seed_users:
        if not auth.usuarios.get_by_email(email):
            auth.registrar(nome, email, senha, True, role)
