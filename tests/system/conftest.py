"""Fixtures dos testes de sistema: a API completa, com banco em memória."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.api.dependencias import obter_data_atual, obter_sessao
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


class RelogioDeTeste:
    """Relógio falso: a "data de hoje" da API é a que o teste definir (RNF11)."""

    def __init__(self, hoje: date):
        self.hoje = hoje

    def avancar(self, dias: int) -> None:
        self.hoje += timedelta(days=dias)


@pytest.fixture
def relogio() -> RelogioDeTeste:
    return RelogioDeTeste(hoje=date(2026, 11, 10))


@pytest.fixture
def cliente(engine, relogio):
    """Cliente HTTP ligado à API, com banco em memória e relógio controlado."""
    fabrica_de_sessoes = sessionmaker(bind=engine)

    with fabrica_de_sessoes() as sessao:
        criar_dados_iniciais(sessao)

    def obter_sessao_de_teste():
        with fabrica_de_sessoes() as sessao:
            yield sessao

    # Troca as dependências reais (arquivo biblioteca.db e relógio do sistema)
    app.dependency_overrides[obter_sessao] = obter_sessao_de_teste
    app.dependency_overrides[obter_data_atual] = lambda: relogio.hoje

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


@pytest.fixture
def exemplares(cliente, cabecalho_aluno) -> list[int]:
    """Ids de todos os exemplares do acervo, obtidos pela própria API."""
    livros = cliente.get("/livros", headers=cabecalho_aluno).json()
    return [exemplar["id"] for livro in livros for exemplar in livro["exemplares"]]


@pytest.fixture
def id_do_aluno(cliente, cabecalho_aluno) -> int:
    """Id do aluno, descoberto pela própria API."""
    return cliente.get("/usuarios/eu", headers=cabecalho_aluno).json()["id"]


@pytest.fixture
def id_do_professor(cliente, cabecalho_professor) -> int:
    """Id do professor, descoberto pela própria API."""
    return cliente.get("/usuarios/eu", headers=cabecalho_professor).json()["id"]
