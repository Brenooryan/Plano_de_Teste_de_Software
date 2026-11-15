"""Rotas de usuário (M1)."""

from fastapi import APIRouter, Depends

from app.api.dependencias import obter_usuario_atual
from app.models import Usuario
from app.schemas.usuarios import UsuarioSaida

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("/eu", response_model=UsuarioSaida)
def consultar_meus_dados(usuario: Usuario = Depends(obter_usuario_atual)) -> UsuarioSaida:
    """Dados do usuário dono do token, incluindo o seu id."""
    return UsuarioSaida.model_validate(usuario)
