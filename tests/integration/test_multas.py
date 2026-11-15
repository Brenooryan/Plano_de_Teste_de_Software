"""Testes de integração de multa, bloqueio e pagamento (RF21 a RF24).

Técnicas: valor limite (pela cadeia completa) e teste baseado em estados
(usuário Ativo <-> Bloqueado).
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.excecoes import NaoEncontradoError, RegraDeNegocioError
from app.services.emprestimos import devolver, emprestar
from app.services.multas import pagar_multa, tem_multa_pendente

HOJE = date(2026, 11, 10)
ID_INEXISTENTE = 999


def devolver_com_atraso(sessao, aluno, exemplar, dias_apos_o_prazo: int):
    """Empresta hoje e devolve N dias depois da data prevista."""
    emprestimo = emprestar(sessao, aluno.id, exemplar.id, HOJE)
    data_devolucao = emprestimo.data_prevista + timedelta(days=dias_apos_o_prazo)
    return devolver(sessao, exemplar.id, data_devolucao)


@pytest.mark.parametrize(
    ("dias_apos_o_prazo", "multa_esperada"),
    [
        (0, None),              # limite: no prazo, sem multa
        (1, Decimal("1.00")),   # limite: primeiro dia cobrado
        (30, Decimal("30.00")), # limite: exatamente no teto
        (31, Decimal("30.00")), # limite: acima do teto
    ],
)
def test_valor_da_multa_gravada_na_devolucao(
    sessao, aluno, exemplar, dias_apos_o_prazo, multa_esperada
):
    _, multa = devolver_com_atraso(sessao, aluno, exemplar, dias_apos_o_prazo)

    valor = multa.valor if multa else None
    assert valor == multa_esperada


def test_multa_nasce_pendente_e_ligada_ao_usuario(sessao, aluno, exemplar):
    emprestimo, multa = devolver_com_atraso(sessao, aluno, exemplar, dias_apos_o_prazo=3)

    assert multa.paga is False
    assert multa.usuario_id == aluno.id
    assert multa.emprestimo_id == emprestimo.id


def test_ciclo_de_estados_do_usuario(sessao, aluno, criar_exemplar):
    # Ativo -> Bloqueado (multa gerada) -> Ativo (multa paga)
    assert tem_multa_pendente(sessao, aluno.id) is False

    _, multa = devolver_com_atraso(sessao, aluno, criar_exemplar(), dias_apos_o_prazo=3)
    assert tem_multa_pendente(sessao, aluno.id) is True  # RF23

    pagar_multa(sessao, multa.id)
    assert tem_multa_pendente(sessao, aluno.id) is False  # RF24


def test_multa_pendente_bloqueia_emprestimo_e_pagamento_libera(sessao, aluno, criar_exemplar):
    # Cadeia entre módulos: devolução atrasada (M4) bloqueia o empréstimo (M3)
    _, multa = devolver_com_atraso(sessao, aluno, criar_exemplar(), dias_apos_o_prazo=3)
    outro_exemplar = criar_exemplar()

    with pytest.raises(RegraDeNegocioError) as erro:
        emprestar(sessao, aluno.id, outro_exemplar.id, HOJE)
    assert erro.value.codigo == "multa_pendente"

    pagar_multa(sessao, multa.id)
    emprestimo = emprestar(sessao, aluno.id, outro_exemplar.id, HOJE)
    assert emprestimo.ativo is True


def test_pagar_multa_ja_paga_e_recusado(sessao, aluno, exemplar):
    _, multa = devolver_com_atraso(sessao, aluno, exemplar, dias_apos_o_prazo=3)
    pagar_multa(sessao, multa.id)

    with pytest.raises(RegraDeNegocioError) as erro:
        pagar_multa(sessao, multa.id)

    assert erro.value.codigo == "multa_ja_paga"


def test_pagar_multa_inexistente(sessao):
    with pytest.raises(NaoEncontradoError):
        pagar_multa(sessao, ID_INEXISTENTE)
