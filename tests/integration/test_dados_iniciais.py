"""Testes de integração dos dados criados na subida da API."""

from sqlalchemy import func, select

from app.dados_iniciais import EXEMPLARES_POR_LIVRO, LIVROS, criar_dados_iniciais
from app.models import Exemplar, Livro, Usuario


def contar(sessao, modelo) -> int:
    return sessao.scalar(select(func.count()).select_from(modelo))


def test_dados_iniciais_nao_sao_duplicados_na_segunda_execucao(sessao):
    # Simula subir a API duas vezes sobre o mesmo banco
    criar_dados_iniciais(sessao)
    criar_dados_iniciais(sessao)

    assert contar(sessao, Usuario) == 3
    assert contar(sessao, Livro) == len(LIVROS)
    assert contar(sessao, Exemplar) == len(LIVROS) * EXEMPLARES_POR_LIVRO
