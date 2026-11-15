"""Conexão com o banco de dados SQLite."""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

URL_BANCO = "sqlite:///./biblioteca.db"


class Base(DeclarativeBase):
    """Classe-base de todos os modelos (tabelas)."""


@event.listens_for(Engine, "connect")
def _ativar_chaves_estrangeiras(conexao_dbapi, _registro):
    """O SQLite só verifica chaves estrangeiras se isto for ligado a cada conexão."""
    cursor = conexao_dbapi.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# check_same_thread=False: o FastAPI atende requisições em mais de uma thread
engine = create_engine(URL_BANCO, connect_args={"check_same_thread": False})

# Fábrica de sessões: cada sessão é uma "conversa" com o banco
SessionLocal = sessionmaker(bind=engine)
