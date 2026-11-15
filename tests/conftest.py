"""Fixtures compartilhadas entre os testes."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registra as tabelas na Base)
from app.database import Base


@pytest.fixture
def engine():
    """Banco SQLite em memória, vazio e exclusivo do teste."""
    # "sqlite://" sem caminho = banco em memória. O StaticPool mantém uma
    # única conexão, para que todos enxerguem o mesmo banco.
    banco = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(banco)

    yield banco

    banco.dispose()


@pytest.fixture
def sessao(engine):
    """Sessão ligada ao banco em memória do teste."""
    with sessionmaker(bind=engine)() as sessao:
        yield sessao
