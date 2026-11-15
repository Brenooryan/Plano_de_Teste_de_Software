"""Testes unitários de hash de senha (RNF02) e de token (RF04 e RF06)."""

from datetime import timedelta

import jwt

from app.seguranca import criar_token, gerar_hash_senha, ler_token, verificar_senha

SENHA = "senha-correta-123"


# --- Senhas ---------------------------------------------------------------


def test_hash_nao_contem_a_senha():
    assert SENHA not in gerar_hash_senha(SENHA)


def test_senha_correta_e_aceita():
    assert verificar_senha(SENHA, gerar_hash_senha(SENHA)) is True


def test_senha_incorreta_e_recusada():
    assert verificar_senha("senha-errada", gerar_hash_senha(SENHA)) is False


def test_mesma_senha_gera_hashes_diferentes():
    # O sal aleatório impede que senhas iguais fiquem iguais no banco
    assert gerar_hash_senha(SENHA) != gerar_hash_senha(SENHA)


def test_hash_malformado_e_recusado():
    assert verificar_senha(SENHA, "isto-nao-e-um-hash") is False


# --- Tokens ---------------------------------------------------------------


def test_token_valido_devolve_o_id_do_usuario():
    assert ler_token(criar_token(usuario_id=7)) == 7


def test_token_expirado_e_recusado():
    token = criar_token(usuario_id=7, validade=timedelta(minutes=-1))

    assert ler_token(token) is None


def test_token_adulterado_e_recusado():
    token = criar_token(usuario_id=7)
    # Troca um caractere no meio da assinatura (o último trecho do token)
    posicao = len(token) - 10
    trocado = "A" if token[posicao] != "A" else "B"
    adulterado = token[:posicao] + trocado + token[posicao + 1 :]

    assert ler_token(adulterado) is None


def test_token_assinado_com_outra_chave_e_recusado():
    falso = jwt.encode({"sub": "7"}, "chave-de-um-atacante-com-mais-de-32-bytes", algorithm="HS256")

    assert ler_token(falso) is None


def test_texto_qualquer_nao_e_token():
    assert ler_token("abc.def.ghi") is None
