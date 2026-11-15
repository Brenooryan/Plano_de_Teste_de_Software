"""Testes de sistema de controle de acesso aos dados (RF08 e RNF02).

Alvo: a falha "controle de acesso quebrado" do OWASP Top 10, em que um
usuário lê dados de outro apenas trocando o id na URL.
"""

ID_INEXISTENTE = 999


def test_usuario_consulta_os_proprios_dados_sem_a_senha(cliente, cabecalho_aluno):
    resposta = cliente.get("/usuarios/eu", headers=cabecalho_aluno)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo.keys()) == {"id", "nome", "email", "perfil", "ativo"}  # RNF02
    assert corpo["perfil"] == "aluno"


def test_consulta_dos_proprios_dados_sem_token(cliente):
    assert cliente.get("/usuarios/eu").status_code == 401


def test_aluno_ve_os_proprios_emprestimos(cliente, cabecalho_aluno, id_do_aluno, exemplares):
    cliente.post("/emprestimos", json={"exemplar_id": exemplares[0]}, headers=cabecalho_aluno)

    resposta = cliente.get(f"/usuarios/{id_do_aluno}/emprestimos", headers=cabecalho_aluno)

    assert resposta.status_code == 200
    assert [e["exemplar_id"] for e in resposta.json()] == [exemplares[0]]


def test_aluno_nao_ve_os_emprestimos_de_outro_usuario(cliente, cabecalho_aluno, id_do_professor):
    resposta = cliente.get(f"/usuarios/{id_do_professor}/emprestimos", headers=cabecalho_aluno)

    assert resposta.status_code == 403


def test_aluno_nao_ve_as_multas_de_outro_usuario(cliente, cabecalho_aluno, id_do_professor):
    resposta = cliente.get(f"/usuarios/{id_do_professor}/multas", headers=cabecalho_aluno)

    assert resposta.status_code == 403


def test_aluno_ve_as_proprias_multas(cliente, cabecalho_aluno, id_do_aluno):
    resposta = cliente.get(f"/usuarios/{id_do_aluno}/multas", headers=cabecalho_aluno)

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_bibliotecario_ve_os_emprestimos_de_qualquer_usuario(
    cliente, cabecalho_aluno, cabecalho_bibliotecario, id_do_aluno, exemplares
):
    cliente.post("/emprestimos", json={"exemplar_id": exemplares[0]}, headers=cabecalho_aluno)

    resposta = cliente.get(f"/usuarios/{id_do_aluno}/emprestimos", headers=cabecalho_bibliotecario)

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_bibliotecario_consulta_usuario_inexistente(cliente, cabecalho_bibliotecario):
    resposta = cliente.get(
        f"/usuarios/{ID_INEXISTENTE}/emprestimos", headers=cabecalho_bibliotecario
    )

    assert resposta.status_code == 404


def test_bibliotecario_consulta_multas_de_usuario_inexistente(cliente, cabecalho_bibliotecario):
    resposta = cliente.get(f"/usuarios/{ID_INEXISTENTE}/multas", headers=cabecalho_bibliotecario)

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Usuário não encontrado"}


def test_aluno_nao_descobre_se_um_id_existe(cliente, cabecalho_aluno):
    # Para quem não tem permissão, id existente e inexistente dão a mesma resposta
    resposta = cliente.get(f"/usuarios/{ID_INEXISTENTE}/emprestimos", headers=cabecalho_aluno)

    assert resposta.status_code == 403


def test_emprestimos_de_usuario_sem_token(cliente):
    assert cliente.get("/usuarios/1/emprestimos").status_code == 401


def test_id_de_usuario_nao_numerico(cliente, cabecalho_bibliotecario):
    # RNF07: entrada mal formada resulta em 422, nunca em 500
    resposta = cliente.get("/usuarios/abc/emprestimos", headers=cabecalho_bibliotecario)

    assert resposta.status_code == 422
