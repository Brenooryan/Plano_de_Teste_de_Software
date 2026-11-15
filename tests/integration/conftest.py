"""Fixtures dos testes de integração: dados básicos já gravados no banco."""

import pytest

from app.enums import Perfil
from app.models import Exemplar, Livro, Usuario


@pytest.fixture
def aluno(sessao) -> Usuario:
    usuario = Usuario(
        nome="Ana Aluna",
        email="ana@exemplo.com",
        senha_hash="hash-de-teste",
        perfil=Perfil.ALUNO,
    )
    sessao.add(usuario)
    sessao.commit()
    return usuario


@pytest.fixture
def livro(sessao) -> Livro:
    livro = Livro(titulo="Dom Casmurro", autor="Machado de Assis", isbn="9788535902778")
    sessao.add(livro)
    sessao.commit()
    return livro


@pytest.fixture
def criar_exemplar(sessao, livro):
    """Devolve uma função que cria exemplares, para testes que precisam de vários."""

    def _criar() -> Exemplar:
        exemplar = Exemplar(livro=livro)
        sessao.add(exemplar)
        sessao.commit()
        return exemplar

    return _criar


@pytest.fixture
def exemplar(criar_exemplar) -> Exemplar:
    return criar_exemplar()
