"""Testes de sistema de empréstimo e devolução (RF07, RF14 a RF20, RNF07).

Abordagem caixa-preta: só requisições HTTP e suas respostas.
"""

ID_INEXISTENTE = 999


def emprestar(cliente, cabecalho, exemplar_id):
    return cliente.post("/emprestimos", json={"exemplar_id": exemplar_id}, headers=cabecalho)


def devolver(cliente, cabecalho, exemplar_id):
    return cliente.post("/devolucoes", json={"exemplar_id": exemplar_id}, headers=cabecalho)


def estado_do_exemplar(cliente, cabecalho, exemplar_id) -> str:
    livros = cliente.get("/livros", headers=cabecalho).json()
    estados = {e["id"]: e["estado"] for livro in livros for e in livro["exemplares"]}
    return estados[exemplar_id]


# --- Empréstimo -----------------------------------------------------------


def test_aluno_empresta_exemplar_disponivel(cliente, cabecalho_aluno, exemplares):
    resposta = emprestar(cliente, cabecalho_aluno, exemplares[0])

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["exemplar_id"] == exemplares[0]
    assert corpo["data_emprestimo"] == "2026-11-10"
    assert corpo["data_prevista"] == "2026-11-17"  # RF16: aluno, 7 dias
    assert corpo["data_devolucao"] is None
    assert estado_do_exemplar(cliente, cabecalho_aluno, exemplares[0]) == "emprestado"  # RF17


def test_professor_recebe_prazo_de_14_dias(cliente, cabecalho_professor, exemplares):
    resposta = emprestar(cliente, cabecalho_professor, exemplares[0])

    assert resposta.status_code == 201
    assert resposta.json()["data_prevista"] == "2026-11-24"  # RF16


def test_emprestimo_sem_token_e_recusado(cliente, exemplares):
    resposta = cliente.post("/emprestimos", json={"exemplar_id": exemplares[0]})

    assert resposta.status_code == 401


def test_bibliotecario_nao_pode_emprestar(cliente, cabecalho_bibliotecario, exemplares):
    # RF18
    resposta = emprestar(cliente, cabecalho_bibliotecario, exemplares[0])

    assert resposta.status_code == 403


def test_emprestar_exemplar_inexistente(cliente, cabecalho_aluno):
    resposta = emprestar(cliente, cabecalho_aluno, ID_INEXISTENTE)

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Exemplar não encontrado"}


def test_emprestar_exemplar_ja_emprestado(
    cliente, cabecalho_aluno, cabecalho_professor, exemplares
):
    emprestar(cliente, cabecalho_aluno, exemplares[0])

    resposta = emprestar(cliente, cabecalho_professor, exemplares[0])

    assert resposta.status_code == 409
    assert resposta.json()["codigo"] == "exemplar_indisponivel"


def test_aluno_tem_o_quarto_emprestimo_recusado(cliente, cabecalho_aluno, exemplares):
    # RF15, valor limite: 3º aceito, 4º recusado
    for exemplar_id in exemplares[:3]:
        assert emprestar(cliente, cabecalho_aluno, exemplar_id).status_code == 201

    resposta = emprestar(cliente, cabecalho_aluno, exemplares[3])

    assert resposta.status_code == 409
    assert resposta.json() == {
        "detail": "Limite de 3 empréstimos ativos atingido",  # RNF06
        "codigo": "limite_atingido",
    }


def test_professor_tem_o_sexto_emprestimo_recusado(cliente, cabecalho_professor, exemplares):
    # RF15, valor limite: 5º aceito, 6º recusado
    for exemplar_id in exemplares[:5]:
        assert emprestar(cliente, cabecalho_professor, exemplar_id).status_code == 201

    resposta = emprestar(cliente, cabecalho_professor, exemplares[5])

    assert resposta.status_code == 409
    assert resposta.json()["codigo"] == "limite_atingido"


def test_emprestimo_com_dado_invalido(cliente, cabecalho_aluno):
    # RNF07: entrada mal formada resulta em 422, nunca em 500
    resposta = cliente.post(
        "/emprestimos", json={"exemplar_id": "nao-e-numero"}, headers=cabecalho_aluno
    )

    assert resposta.status_code == 422


# --- Devolução ------------------------------------------------------------


def test_bibliotecario_registra_devolucao_no_prazo(
    cliente, cabecalho_aluno, cabecalho_bibliotecario, exemplares
):
    emprestar(cliente, cabecalho_aluno, exemplares[0])

    resposta = devolver(cliente, cabecalho_bibliotecario, exemplares[0])

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["emprestimo"]["data_devolucao"] == "2026-11-10"
    assert corpo["multa"] is None
    assert estado_do_exemplar(cliente, cabecalho_aluno, exemplares[0]) == "disponivel"  # RF19


def test_aluno_nao_pode_registrar_devolucao(cliente, cabecalho_aluno, exemplares):
    # RF07: operação exclusiva do bibliotecário
    emprestar(cliente, cabecalho_aluno, exemplares[0])

    resposta = devolver(cliente, cabecalho_aluno, exemplares[0])

    assert resposta.status_code == 403
    assert estado_do_exemplar(cliente, cabecalho_aluno, exemplares[0]) == "emprestado"


def test_devolver_exemplar_que_nao_esta_emprestado(cliente, cabecalho_bibliotecario, exemplares):
    # RF20: transição de estado inválida
    resposta = devolver(cliente, cabecalho_bibliotecario, exemplares[0])

    assert resposta.status_code == 409
    assert resposta.json()["codigo"] == "exemplar_nao_emprestado"


def test_devolver_exemplar_inexistente(cliente, cabecalho_bibliotecario):
    resposta = devolver(cliente, cabecalho_bibliotecario, ID_INEXISTENTE)

    assert resposta.status_code == 404
