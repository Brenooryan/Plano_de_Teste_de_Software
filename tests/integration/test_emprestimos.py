"""Testes de integração de empréstimo e devolução (RF14 a RF20).

Técnica principal: teste baseado em estados (exemplar Disponível <-> Emprestado).
"""

from datetime import date

import pytest

from app.enums import EstadoExemplar
from app.excecoes import NaoEncontradoError, RegraDeNegocioError
from app.services.emprestimos import contar_emprestimos_ativos, devolver, emprestar

HOJE = date(2026, 11, 10)
ID_INEXISTENTE = 999


# --- Empréstimo -----------------------------------------------------------


def test_emprestar_grava_emprestimo_e_muda_estado_do_exemplar(sessao, aluno, exemplar):
    emprestimo = emprestar(sessao, aluno.id, exemplar.id, HOJE)

    assert emprestimo.ativo is True
    assert emprestimo.data_prevista == date(2026, 11, 17)  # RF16: aluno, 7 dias
    assert exemplar.estado == EstadoExemplar.EMPRESTADO  # RF17


def test_exemplar_emprestado_nao_pode_ser_emprestado_de_novo(sessao, aluno, exemplar):
    emprestar(sessao, aluno.id, exemplar.id, HOJE)

    with pytest.raises(RegraDeNegocioError) as erro:
        emprestar(sessao, aluno.id, exemplar.id, HOJE)

    assert erro.value.codigo == "exemplar_indisponivel"
    assert contar_emprestimos_ativos(sessao, aluno.id) == 1  # RNF05


def test_aluno_no_limite_tem_o_quarto_emprestimo_recusado(sessao, aluno, criar_exemplar):
    for _ in range(3):
        emprestar(sessao, aluno.id, criar_exemplar().id, HOJE)
    quarto_exemplar = criar_exemplar()

    with pytest.raises(RegraDeNegocioError) as erro:
        emprestar(sessao, aluno.id, quarto_exemplar.id, HOJE)

    assert erro.value.codigo == "limite_atingido"
    assert erro.value.mensagem == "Limite de 3 empréstimos ativos atingido"  # RNF06
    assert quarto_exemplar.estado == EstadoExemplar.DISPONIVEL  # recusa não altera nada


def test_devolucao_libera_vaga_no_limite(sessao, aluno, criar_exemplar):
    exemplares = [criar_exemplar() for _ in range(4)]
    for exemplar in exemplares[:3]:
        emprestar(sessao, aluno.id, exemplar.id, HOJE)

    devolver(sessao, exemplares[0].id, HOJE)
    emprestimo = emprestar(sessao, aluno.id, exemplares[3].id, HOJE)

    assert emprestimo.ativo is True
    assert contar_emprestimos_ativos(sessao, aluno.id) == 3


def test_usuario_inativo_nao_pode_emprestar(sessao, aluno, exemplar):
    aluno.ativo = False
    sessao.commit()

    with pytest.raises(RegraDeNegocioError) as erro:
        emprestar(sessao, aluno.id, exemplar.id, HOJE)

    assert erro.value.codigo == "conta_inativa"


def test_emprestar_para_usuario_inexistente(sessao, exemplar):
    with pytest.raises(NaoEncontradoError):
        emprestar(sessao, ID_INEXISTENTE, exemplar.id, HOJE)


def test_emprestar_exemplar_inexistente(sessao, aluno):
    with pytest.raises(NaoEncontradoError):
        emprestar(sessao, aluno.id, ID_INEXISTENTE, HOJE)


# --- Devolução ------------------------------------------------------------


def test_devolucao_no_prazo_encerra_emprestimo_sem_multa(sessao, aluno, exemplar):
    emprestado = emprestar(sessao, aluno.id, exemplar.id, HOJE)

    emprestimo, multa = devolver(sessao, exemplar.id, emprestado.data_prevista)

    assert emprestimo.ativo is False
    assert multa is None
    assert exemplar.estado == EstadoExemplar.DISPONIVEL  # RF19


def test_devolver_exemplar_disponivel_e_recusado(sessao, exemplar):
    # RF20: transição inválida (Disponível -> devolução)
    with pytest.raises(RegraDeNegocioError) as erro:
        devolver(sessao, exemplar.id, HOJE)

    assert erro.value.codigo == "exemplar_nao_emprestado"
    assert exemplar.estado == EstadoExemplar.DISPONIVEL


def test_devolver_exemplar_inexistente(sessao):
    with pytest.raises(NaoEncontradoError):
        devolver(sessao, ID_INEXISTENTE, HOJE)


def test_ciclo_de_estados_do_exemplar(sessao, aluno, exemplar):
    # Disponível -> Emprestado -> Disponível -> Emprestado
    assert exemplar.estado == EstadoExemplar.DISPONIVEL

    emprestar(sessao, aluno.id, exemplar.id, HOJE)
    assert exemplar.estado == EstadoExemplar.EMPRESTADO

    devolver(sessao, exemplar.id, HOJE)
    assert exemplar.estado == EstadoExemplar.DISPONIVEL

    emprestar(sessao, aluno.id, exemplar.id, HOJE)
    assert exemplar.estado == EstadoExemplar.EMPRESTADO
