"""Testes de sistema da consulta ao acervo."""

from app.dados_iniciais import EXEMPLARES_POR_LIVRO, LIVROS


def test_usuario_autenticado_lista_os_livros(cliente, cabecalho_aluno):
    resposta = cliente.get("/livros", headers=cabecalho_aluno)

    assert resposta.status_code == 200
    livros = resposta.json()
    assert len(livros) == len(LIVROS)
    for livro in livros:
        assert livro["disponiveis"] == EXEMPLARES_POR_LIVRO
        assert len(livro["exemplares"]) == EXEMPLARES_POR_LIVRO
        assert all(exemplar["estado"] == "disponivel" for exemplar in livro["exemplares"])


def test_resposta_do_acervo_tem_apenas_os_campos_publicos(cliente, cabecalho_aluno):
    resposta = cliente.get("/livros", headers=cabecalho_aluno)

    campos = set(resposta.json()[0].keys())
    assert campos == {"id", "titulo", "autor", "isbn", "disponiveis", "exemplares"}
