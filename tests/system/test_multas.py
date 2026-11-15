"""Testes de sistema e de aceitação de multa e bloqueio (RF07, RF21 a RF24)."""

import pytest

ID_INEXISTENTE = 999
PRAZO_DO_ALUNO = 7


def emprestar(cliente, cabecalho, exemplar_id):
    return cliente.post("/emprestimos", json={"exemplar_id": exemplar_id}, headers=cabecalho)


def devolver_com_atraso(
    cliente, relogio, cabecalho_aluno, cabecalho_bibliotecario, exemplar_id, dias
):
    """O aluno empresta hoje e o bibliotecário devolve N dias depois do prazo."""
    assert emprestar(cliente, cabecalho_aluno, exemplar_id).status_code == 201
    relogio.avancar(dias=PRAZO_DO_ALUNO + dias)
    resposta = cliente.post(
        "/devolucoes", json={"exemplar_id": exemplar_id}, headers=cabecalho_bibliotecario
    )
    assert resposta.status_code == 200
    return resposta.json()


@pytest.mark.parametrize(
    ("dias_de_atraso", "valor_esperado"),
    [
        (1, "1.00"),    # limite: primeiro dia cobrado
        (30, "30.00"),  # limite: exatamente no teto
        (31, "30.00"),  # limite: acima do teto
    ],
)
def test_devolucao_atrasada_gera_multa(
    cliente,
    relogio,
    cabecalho_aluno,
    cabecalho_bibliotecario,
    exemplares,
    dias_de_atraso,
    valor_esperado,
):
    devolucao = devolver_com_atraso(
        cliente, relogio, cabecalho_aluno, cabecalho_bibliotecario, exemplares[0], dias_de_atraso
    )

    assert devolucao["multa"]["valor"] == valor_esperado
    assert devolucao["multa"]["paga"] is False


def test_aceitacao_multa_bloqueia_e_pagamento_libera(
    cliente, relogio, cabecalho_aluno, cabecalho_bibliotecario, exemplares
):
    # DADO um aluno que devolveu um livro com 3 dias de atraso
    devolucao = devolver_com_atraso(
        cliente, relogio, cabecalho_aluno, cabecalho_bibliotecario, exemplares[0], dias=3
    )
    multa = devolucao["multa"]
    assert multa["valor"] == "3.00"

    # QUANDO ele tenta um novo empréstimo
    recusa = emprestar(cliente, cabecalho_aluno, exemplares[1])

    # ENTÃO o sistema recusa por multa pendente
    assert recusa.status_code == 409
    assert recusa.json() == {"detail": "Usuário com multa pendente", "codigo": "multa_pendente"}

    # QUANDO o bibliotecário registra o pagamento da multa
    pagamento = cliente.post(f"/multas/{multa['id']}/pagamento", headers=cabecalho_bibliotecario)
    assert pagamento.status_code == 200
    assert pagamento.json()["paga"] is True

    # ENTÃO o aluno volta a poder emprestar
    assert emprestar(cliente, cabecalho_aluno, exemplares[1]).status_code == 201


def test_aluno_nao_pode_registrar_pagamento(
    cliente, relogio, cabecalho_aluno, cabecalho_bibliotecario, exemplares
):
    # RF07: um aluno não pode quitar a própria multa
    devolucao = devolver_com_atraso(
        cliente, relogio, cabecalho_aluno, cabecalho_bibliotecario, exemplares[0], dias=3
    )

    resposta = cliente.post(
        f"/multas/{devolucao['multa']['id']}/pagamento", headers=cabecalho_aluno
    )

    assert resposta.status_code == 403


def test_pagar_a_mesma_multa_duas_vezes(
    cliente, relogio, cabecalho_aluno, cabecalho_bibliotecario, exemplares
):
    devolucao = devolver_com_atraso(
        cliente, relogio, cabecalho_aluno, cabecalho_bibliotecario, exemplares[0], dias=3
    )
    rota = f"/multas/{devolucao['multa']['id']}/pagamento"
    cliente.post(rota, headers=cabecalho_bibliotecario)

    resposta = cliente.post(rota, headers=cabecalho_bibliotecario)

    assert resposta.status_code == 409
    assert resposta.json()["codigo"] == "multa_ja_paga"


def test_pagar_multa_inexistente(cliente, cabecalho_bibliotecario):
    resposta = cliente.post(
        f"/multas/{ID_INEXISTENTE}/pagamento", headers=cabecalho_bibliotecario
    )

    assert resposta.status_code == 404
