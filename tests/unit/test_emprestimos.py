"""Testes unitários das regras de empréstimo (RF14, RF15, RF16 e RF18).

Técnicas: tabela de decisão, análise do valor limite e partição de
equivalência.
"""

from datetime import date

import pytest

from app.enums import EstadoExemplar, Perfil
from app.regras.emprestimos import (
    MotivoRecusa,
    calcular_data_prevista,
    verificar_emprestimo,
)

S, N = True, False


# --- RF14: tabela de decisão ----------------------------------------------
# Quatro condições (S = atendida, N = não atendida) geram 2^4 = 16 regras.
# Todas são testadas. Quando mais de uma condição falha, o motivo informado
# é o da primeira na ordem: conta > multa > limite > exemplar.


@pytest.mark.parametrize(
    ("conta_ativa", "sem_multa", "abaixo_do_limite", "exemplar_disponivel", "esperado"),
    [
        # conta  multa  limite  exemplar   resultado esperado
        (S, S, S, S, None),
        (S, S, S, N, MotivoRecusa.EXEMPLAR_INDISPONIVEL),
        (S, S, N, S, MotivoRecusa.LIMITE_ATINGIDO),
        (S, S, N, N, MotivoRecusa.LIMITE_ATINGIDO),
        (S, N, S, S, MotivoRecusa.MULTA_PENDENTE),
        (S, N, S, N, MotivoRecusa.MULTA_PENDENTE),
        (S, N, N, S, MotivoRecusa.MULTA_PENDENTE),
        (S, N, N, N, MotivoRecusa.MULTA_PENDENTE),
        (N, S, S, S, MotivoRecusa.CONTA_INATIVA),
        (N, S, S, N, MotivoRecusa.CONTA_INATIVA),
        (N, S, N, S, MotivoRecusa.CONTA_INATIVA),
        (N, S, N, N, MotivoRecusa.CONTA_INATIVA),
        (N, N, S, S, MotivoRecusa.CONTA_INATIVA),
        (N, N, S, N, MotivoRecusa.CONTA_INATIVA),
        (N, N, N, S, MotivoRecusa.CONTA_INATIVA),
        (N, N, N, N, MotivoRecusa.CONTA_INATIVA),
    ],
)
def test_tabela_de_decisao_do_emprestimo(
    conta_ativa, sem_multa, abaixo_do_limite, exemplar_disponivel, esperado
):
    # Arrange: converte cada condição da tabela em um dado concreto (aluno)
    emprestimos_ativos = 0 if abaixo_do_limite else 3
    estado = EstadoExemplar.DISPONIVEL if exemplar_disponivel else EstadoExemplar.EMPRESTADO

    # Act
    resultado = verificar_emprestimo(
        perfil=Perfil.ALUNO,
        conta_ativa=conta_ativa,
        tem_multa_pendente=not sem_multa,
        emprestimos_ativos=emprestimos_ativos,
        estado_exemplar=estado,
    )

    # Assert
    assert resultado == esperado


# --- RF15: valor limite da quantidade de empréstimos ativos ---------------
# Aluno: limite 3. Professor: limite 5.


@pytest.mark.parametrize(
    ("perfil", "emprestimos_ativos", "esperado"),
    [
        (Perfil.ALUNO, 0, None),                              # mínimo
        (Perfil.ALUNO, 2, None),                              # pede o 3º: aceito
        (Perfil.ALUNO, 3, MotivoRecusa.LIMITE_ATINGIDO),      # pede o 4º: recusado
        (Perfil.ALUNO, 4, MotivoRecusa.LIMITE_ATINGIDO),      # acima do limite
        (Perfil.PROFESSOR, 3, None),                          # limite do aluno não vale aqui
        (Perfil.PROFESSOR, 4, None),                          # pede o 5º: aceito
        (Perfil.PROFESSOR, 5, MotivoRecusa.LIMITE_ATINGIDO),  # pede o 6º: recusado
        (Perfil.PROFESSOR, 6, MotivoRecusa.LIMITE_ATINGIDO),  # acima do limite
    ],
)
def test_limite_de_emprestimos_por_perfil(perfil, emprestimos_ativos, esperado):
    resultado = verificar_emprestimo(
        perfil=perfil,
        conta_ativa=True,
        tem_multa_pendente=False,
        emprestimos_ativos=emprestimos_ativos,
        estado_exemplar=EstadoExemplar.DISPONIVEL,
    )

    assert resultado == esperado


# --- RF18: bibliotecário não empresta -------------------------------------


def test_bibliotecario_nao_pode_emprestar():
    resultado = verificar_emprestimo(
        perfil=Perfil.BIBLIOTECARIO,
        conta_ativa=True,
        tem_multa_pendente=False,
        emprestimos_ativos=0,
        estado_exemplar=EstadoExemplar.DISPONIVEL,
    )

    assert resultado == MotivoRecusa.PERFIL_NAO_PERMITIDO


# --- RF16: data prevista de devolução -------------------------------------
# Partições: aluno (7 dias corridos) | professor (14 dias corridos)


@pytest.mark.parametrize(
    ("perfil", "data_emprestimo", "data_esperada"),
    [
        (Perfil.ALUNO, date(2026, 11, 10), date(2026, 11, 17)),
        (Perfil.PROFESSOR, date(2026, 11, 10), date(2026, 11, 24)),
        (Perfil.ALUNO, date(2026, 12, 28), date(2027, 1, 4)),       # virada de ano
        (Perfil.PROFESSOR, date(2026, 12, 28), date(2027, 1, 11)),  # virada de ano
    ],
)
def test_data_prevista_de_devolucao(perfil, data_emprestimo, data_esperada):
    assert calcular_data_prevista(perfil, data_emprestimo) == data_esperada


def test_data_prevista_recusa_perfil_sem_prazo():
    with pytest.raises(ValueError):
        calcular_data_prevista(Perfil.BIBLIOTECARIO, date(2026, 11, 10))
