"""Fixtures dos testes de sistema: a API completa, com banco em memória."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.api.dependencias import obter_sessao
from app.dados_iniciais import (
    EMAIL_ALUNO,
    EMAIL_BIBLIOTECARIO,
    EMAIL_PROFESSOR,
    SENHA_ALUNO,
    SENHA_BIBLIOTECARIO,
    SENHA_PROFESSOR,
    criar_dados_iniciais,
)
from app.main import app


@pytest.fixture
def cliente(engine):
    """Cliente HTTP ligado à API, usando o banco em memória do teste."""
    fabrica_de_sessoes = sessionmaker(bind=engine)

    with fabrica_de_sessoes() as sessao:
        criar_dados_iniciais(sessao)

    def obter_sessao_de_teste():
        with fabrica_de_sessoes() as sessao:
            yield sessao

    # Troca a dependência real (arquivo biblioteca.db) pela de teste
    app.dependency_overrides[obter_sessao] = obter_sessao_de_teste

    yield TestClient(app)

    app.dependency_overrides.clear()


def fazer_login(cliente: TestClient, email: str, senha: str) -> dict[str, str]:
    """Faz login e devolve o cabeçalho Authorization pronto para uso."""
    resposta = cliente.post("/auth/login", json={"email": email, "senha": senha})
    assert resposta.status_code == 200, resposta.text
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


@pytest.fixture
def cabecalho_aluno(cliente) -> dict[str, str]:
    return fazer_login(cliente, EMAIL_ALUNO, SENHA_ALUNO)


@pytest.fixture
def cabecalho_professor(cliente) -> dict[str, str]:
    return fazer_login(cliente, EMAIL_PROFESSOR, SENHA_PROFESSOR)


@pytest.fixture
def cabecalho_bibliotecario(cliente) -> dict[str, str]:
    return fazer_login(cliente, EMAIL_BIBLIOTECARIO, SENHA_BIBLIOTECARIO)
