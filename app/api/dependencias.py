"""Dependências compartilhadas pelas rotas.

No FastAPI, uma dependência é uma função que a rota declara com Depends().
O framework a executa antes da rota e entrega o resultado como parâmetro.
Nos testes, cada dependência pode ser trocada por outra.
"""

from collections.abc import Iterator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Usuario
from app.seguranca import ler_token

# Lê o cabeçalho "Authorization: Bearer <token>". Com auto_error=False,
# a ausência do cabeçalho chega aqui como None e nós decidimos a resposta.
_esquema_bearer = HTTPBearer(auto_error=False)


def obter_sessao() -> Iterator[Session]:
    """Abre uma sessão do banco para a requisição e a fecha ao final."""
    with SessionLocal() as sessao:
        yield sessao


def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(_esquema_bearer),
    sessao: Session = Depends(obter_sessao),
) -> Usuario:
    """RF06: identifica o usuário pelo token ou recusa com 401."""
    nao_autenticado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado: token ausente, inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credenciais is None:
        raise nao_autenticado

    usuario_id = ler_token(credenciais.credentials)
    if usuario_id is None:
        raise nao_autenticado

    usuario = sessao.get(Usuario, usuario_id)
    if usuario is None:
        raise nao_autenticado

    return usuario
