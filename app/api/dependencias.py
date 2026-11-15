"""Dependências compartilhadas pelas rotas.

No FastAPI, uma dependência é uma função que a rota declara com Depends().
O framework a executa antes da rota e entrega o resultado como parâmetro.
Nos testes, cada dependência pode ser trocada por outra.
"""

from collections.abc import Callable, Iterator
from datetime import date
from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import MAIOR_ID
from app.database import SessionLocal
from app.enums import Perfil
from app.models import Usuario
from app.relogio import data_atual
from app.seguranca import ler_token

# Lê o cabeçalho "Authorization: Bearer <token>". Com auto_error=False,
# a ausência do cabeçalho chega aqui como None e nós decidimos a resposta.
_esquema_bearer = HTTPBearer(auto_error=False)

_SEM_PERMISSAO = "Sem permissão para esta operação"

# Correção do DEF-02: identificador recebido no caminho da URL, com faixa válida.
# Fora dela, a própria validação responde 422, antes de chegar ao banco.
IdNoCaminho = Annotated[int, Path(ge=1, le=MAIOR_ID)]


def obter_sessao() -> Iterator[Session]:
    """Abre uma sessão do banco para a requisição e a fecha ao final."""
    with SessionLocal() as sessao:
        yield sessao


def obter_data_atual() -> date:
    """RNF11: a data de hoje. Nos testes, é trocada por um relógio controlado."""
    return data_atual()


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


def exigir_perfil(*perfis_permitidos: Perfil) -> Callable[..., Usuario]:
    """RF07: cria uma dependência que só aceita os perfis informados (senão, 403)."""

    def verificar(usuario: Usuario = Depends(obter_usuario_atual)) -> Usuario:
        if usuario.perfil not in perfis_permitidos:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_SEM_PERMISSAO)
        return usuario

    return verificar


apenas_bibliotecario = exigir_perfil(Perfil.BIBLIOTECARIO)
apenas_leitores = exigir_perfil(Perfil.ALUNO, Perfil.PROFESSOR)


def proprio_usuario_ou_bibliotecario(
    usuario_id: IdNoCaminho,
    usuario: Usuario = Depends(obter_usuario_atual),
) -> Usuario:
    """RF08: cada um vê só os próprios dados; o bibliotecário vê os de todos.

    O usuario_id vem do caminho da rota (/usuarios/{usuario_id}/...).
    """
    if usuario.perfil != Perfil.BIBLIOTECARIO and usuario.id != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_SEM_PERMISSAO)
    return usuario
