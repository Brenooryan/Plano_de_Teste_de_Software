"""Rotas de autenticação (M1)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencias import obter_sessao
from app.schemas.auth import LoginEntrada, TokenSaida
from app.seguranca import criar_token
from app.services.usuarios import autenticar

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenSaida)
def login(dados: LoginEntrada, sessao: Session = Depends(obter_sessao)) -> TokenSaida:
    """Troca e-mail e senha por um token de acesso válido por 30 minutos."""
    usuario = autenticar(sessao, dados.email, dados.senha)

    if usuario is None:
        # RF05: mesma mensagem para e-mail inexistente e para senha errada
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )

    return TokenSaida(access_token=criar_token(usuario.id))
