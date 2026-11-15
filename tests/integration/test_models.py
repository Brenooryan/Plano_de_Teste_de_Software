"""Testes de integração dos modelos: tabelas, valores padrão e restrições."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.enums import EstadoExemplar, Perfil
from app.models import Emprestimo, Exemplar, Livro, Multa, Usuario


def novo_usuario(email: str = "ana@exemplo.com") -> Usuario:
    return Usuario(nome="Ana", email=email, senha_hash="hash-de-teste", perfil=Perfil.ALUNO)


def novo_livro(isbn: str = "9788535902778") -> Livro:
    return Livro(titulo="Dom Casmurro", autor="Machado de Assis", isbn=isbn)


@pytest.fixture
def emprestimo(sessao) -> Emprestimo:
    """Um empréstimo ativo, já gravado, com usuário, livro e exemplar."""
    emprestimo = Emprestimo(
        usuario=novo_usuario(),
        exemplar=Exemplar(livro=novo_livro()),
        data_emprestimo=date(2026, 11, 3),
        data_prevista=date(2026, 11, 10),
    )
    sessao.add(emprestimo)
    sessao.commit()
    return emprestimo


# --- Usuário --------------------------------------------------------------


def test_usuario_e_gravado_com_valores_padrao(sessao):
    sessao.add(novo_usuario())
    sessao.commit()

    usuario = sessao.scalars(select(Usuario)).one()

    assert usuario.id is not None
    assert usuario.perfil == Perfil.ALUNO
    assert usuario.ativo is True


def test_email_duplicado_e_recusado(sessao):
    # RF03
    sessao.add(novo_usuario(email="ana@exemplo.com"))
    sessao.commit()

    sessao.add(novo_usuario(email="ana@exemplo.com"))

    with pytest.raises(IntegrityError):
        sessao.commit()


# --- Acervo ---------------------------------------------------------------


def test_isbn_duplicado_e_recusado(sessao):
    # RF10
    sessao.add(novo_livro(isbn="9788535902778"))
    sessao.commit()

    sessao.add(novo_livro(isbn="9788535902778"))

    with pytest.raises(IntegrityError):
        sessao.commit()


def test_exemplar_novo_inicia_disponivel(sessao):
    # RF11
    sessao.add(Exemplar(livro=novo_livro()))
    sessao.commit()

    exemplar = sessao.scalars(select(Exemplar)).one()

    assert exemplar.estado == EstadoExemplar.DISPONIVEL


def test_exemplar_de_livro_inexistente_e_recusado(sessao):
    # Prova que o banco está verificando as chaves estrangeiras
    sessao.add(Exemplar(livro_id=999))

    with pytest.raises(IntegrityError):
        sessao.commit()


# --- Empréstimo -----------------------------------------------------------


def test_emprestimo_novo_esta_ativo(emprestimo):
    assert emprestimo.data_devolucao is None
    assert emprestimo.ativo is True


def test_emprestimo_devolvido_deixa_de_estar_ativo(sessao, emprestimo):
    emprestimo.data_devolucao = date(2026, 11, 9)
    sessao.commit()

    assert emprestimo.ativo is False


# --- Multa ----------------------------------------------------------------


def test_multa_nova_esta_pendente_e_converte_centavos(sessao, emprestimo):
    sessao.add(Multa(emprestimo=emprestimo, usuario=emprestimo.usuario, valor_centavos=3000))
    sessao.commit()

    multa = sessao.scalars(select(Multa)).one()

    assert multa.paga is False
    assert multa.valor == Decimal("30.00")


def test_segunda_multa_para_o_mesmo_emprestimo_e_recusada(sessao, emprestimo):
    sessao.add(Multa(emprestimo=emprestimo, usuario=emprestimo.usuario, valor_centavos=100))
    sessao.commit()

    sessao.add(Multa(emprestimo=emprestimo, usuario=emprestimo.usuario, valor_centavos=200))

    with pytest.raises(IntegrityError):
        sessao.commit()
