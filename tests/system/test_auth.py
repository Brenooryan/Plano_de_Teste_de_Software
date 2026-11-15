"""Testes de sistema de autenticação (RF04, RF05, RF06 e RNF07).

Abordagem caixa-preta: só requisições HTTP e suas respostas.
"""

from datetime import timedelta

from app.dados_iniciais import EMAIL_ALUNO, SENHA_ALUNO
from app.seguranca import criar_token

ID_INEXISTENTE = 999


# --- Login ----------------------------------------------------------------


def test_login_valido_devolve_token(cliente):
    resposta = cliente.post("/auth/login", json={"email": EMAIL_ALUNO, "senha": SENHA_ALUNO})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert len(corpo["access_token"]) > 0


def test_login_com_senha_errada_e_recusado(cliente):
    resposta = cliente.post("/auth/login", json={"email": EMAIL_ALUNO, "senha": "senha-errada"})

    assert resposta.status_code == 401
    assert resposta.json() == {"detail": "E-mail ou senha incorretos"}


def test_login_nao_revela_se_o_email_existe(cliente):
    # RF05: e-mail inexistente e senha errada produzem respostas idênticas
    senha_errada = cliente.post(
        "/auth/login", json={"email": EMAIL_ALUNO, "senha": "senha-errada"}
    )
    email_inexistente = cliente.post(
        "/auth/login", json={"email": "ninguem@biblioteca.local", "senha": "senha-errada"}
    )

    assert email_inexistente.status_code == senha_errada.status_code == 401
    assert email_inexistente.json() == senha_errada.json()


def test_login_sem_o_campo_senha_e_dado_invalido(cliente):
    # RNF07: entrada mal formada resulta em 422, nunca em 500
    resposta = cliente.post("/auth/login", json={"email": EMAIL_ALUNO})

    assert resposta.status_code == 422


# --- Acesso a rota protegida ----------------------------------------------


def test_rota_protegida_sem_token_e_recusada(cliente):
    resposta = cliente.get("/livros")

    assert resposta.status_code == 401


def test_rota_protegida_com_token_invalido_e_recusada(cliente):
    resposta = cliente.get("/livros", headers={"Authorization": "Bearer token-inventado"})

    assert resposta.status_code == 401


def test_rota_protegida_com_token_expirado_e_recusada(cliente):
    expirado = criar_token(usuario_id=1, validade=timedelta(minutes=-1))

    resposta = cliente.get("/livros", headers={"Authorization": f"Bearer {expirado}"})

    assert resposta.status_code == 401


def test_rota_protegida_com_esquema_diferente_de_bearer_e_recusada(cliente):
    resposta = cliente.get("/livros", headers={"Authorization": "Basic YWx1bm86MTIzNA=="})

    assert resposta.status_code == 401


def test_token_de_usuario_que_nao_existe_e_recusado(cliente):
    token = criar_token(usuario_id=ID_INEXISTENTE)

    resposta = cliente.get("/livros", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 401
