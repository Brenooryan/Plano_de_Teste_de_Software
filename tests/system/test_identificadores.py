"""Testes de valor limite dos identificadores (RNF07).

Hipótese investigada: a API aceita identificadores maiores do que o banco
de dados consegue armazenar. O maior inteiro que o SQLite guarda é 2^63 - 1.

Abordagem caixa-cinza: o limite testado vem do conhecimento do armazenamento
interno, e não da documentação da API.
"""

import pytest

MAIOR_ID = 2**63 - 1  # 9223372036854775807

ROTAS_COM_ID_NO_CAMINHO = [
    ("GET", "/usuarios/{id}/emprestimos"),
    ("GET", "/usuarios/{id}/multas"),
    ("POST", "/multas/{id}/pagamento"),
]


# --- Identificador no caminho da URL --------------------------------------


@pytest.mark.parametrize(("metodo", "rota"), ROTAS_COM_ID_NO_CAMINHO)
def test_id_no_caminho_no_limite_superior_e_valido(
    cliente, cabecalho_bibliotecario, metodo, rota
):
    resposta = cliente.request(
        metodo, rota.format(id=MAIOR_ID), headers=cabecalho_bibliotecario
    )

    assert resposta.status_code == 404  # valor válido, mas o recurso não existe


@pytest.mark.parametrize(("metodo", "rota"), ROTAS_COM_ID_NO_CAMINHO)
def test_id_no_caminho_acima_do_limite_superior_e_dado_invalido(
    cliente, cabecalho_bibliotecario, metodo, rota
):
    resposta = cliente.request(
        metodo, rota.format(id=MAIOR_ID + 1), headers=cabecalho_bibliotecario
    )

    assert resposta.status_code == 422  # RNF07: entrada inválida nunca resulta em 500


@pytest.mark.parametrize(("metodo", "rota"), ROTAS_COM_ID_NO_CAMINHO)
def test_id_no_caminho_abaixo_do_limite_inferior_e_dado_invalido(
    cliente, cabecalho_bibliotecario, metodo, rota
):
    # Identificadores começam em 1: zero está fora da faixa válida
    resposta = cliente.request(metodo, rota.format(id=0), headers=cabecalho_bibliotecario)

    assert resposta.status_code == 422


# --- Identificador no corpo da requisição ---------------------------------


@pytest.mark.parametrize(
    ("exemplar_id", "status_esperado"),
    [
        (MAIOR_ID, 404),      # limite superior: válido, mas não existe
        (MAIOR_ID + 1, 422),  # um acima do limite superior
        (0, 422),             # um abaixo do limite inferior
    ],
)
def test_limites_do_exemplar_na_devolucao(
    cliente, cabecalho_bibliotecario, exemplar_id, status_esperado
):
    resposta = cliente.post(
        "/devolucoes", json={"exemplar_id": exemplar_id}, headers=cabecalho_bibliotecario
    )

    assert resposta.status_code == status_esperado


@pytest.mark.parametrize(
    ("exemplar_id", "status_esperado"),
    [
        (MAIOR_ID, 404),
        (MAIOR_ID + 1, 422),
        (0, 422),
    ],
)
def test_limites_do_exemplar_no_emprestimo(
    cliente, cabecalho_aluno, exemplar_id, status_esperado
):
    resposta = cliente.post(
        "/emprestimos", json={"exemplar_id": exemplar_id}, headers=cabecalho_aluno
    )

    assert resposta.status_code == status_esperado
