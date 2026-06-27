"""Configuração do SQLAlchemy (engine, session, Base declarativa)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# `check_same_thread` é necessário apenas para SQLite.
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    """Cria as tabelas. Importa os models para registrá-los na metadata."""
    from app.infrastructure import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
