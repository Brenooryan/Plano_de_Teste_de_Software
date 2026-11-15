"""Hash de senhas (RNF02) e tokens de acesso (RF04 e RF06)."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.config import CHAVE_SECRETA, VALIDADE_TOKEN_MINUTOS

# --- Senhas ---------------------------------------------------------------
# scrypt: algoritmo feito para senhas, lento de propósito. Os parâmetros
# abaixo definem o custo de cada cálculo (processamento e memória).
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


def _derivar(senha: str, sal: bytes) -> bytes:
    return hashlib.scrypt(
        senha.encode("utf-8"), salt=sal, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P
    )


def gerar_hash_senha(senha: str) -> str:
    """Devolve "sal$hash" em hexadecimal. O sal é aleatório a cada chamada."""
    sal = secrets.token_bytes(16)
    return f"{sal.hex()}${_derivar(senha, sal).hex()}"


def verificar_senha(senha: str, hash_guardado: str) -> bool:
    """Recalcula o hash com o sal guardado e compara com o valor guardado."""
    try:
        sal_hex, derivado_hex = hash_guardado.split("$")
        sal = bytes.fromhex(sal_hex)
        esperado = bytes.fromhex(derivado_hex)
    except ValueError:
        return False

    # compare_digest leva o mesmo tempo acerte ou erre, o que impede que o
    # tempo de resposta revele quantos caracteres estavam corretos
    return hmac.compare_digest(_derivar(senha, sal), esperado)


# --- Tokens (JWT) ---------------------------------------------------------
_ALGORITMO = "HS256"


def criar_token(
    usuario_id: int,
    validade: timedelta = timedelta(minutes=VALIDADE_TOKEN_MINUTOS),
) -> str:
    """RF04: token assinado que identifica o usuário e expira após a validade."""
    dados = {
        "sub": str(usuario_id),
        "exp": datetime.now(timezone.utc) + validade,
    }
    return jwt.encode(dados, CHAVE_SECRETA, algorithm=_ALGORITMO)


def ler_token(token: str) -> int | None:
    """RF06: devolve o id do usuário, ou None se o token for inválido ou expirado."""
    try:
        dados = jwt.decode(token, CHAVE_SECRETA, algorithms=[_ALGORITMO])
        return int(dados["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None
