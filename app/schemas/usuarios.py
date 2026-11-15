"""Formato de saída de usuário. Não existe campo de senha aqui (RNF02)."""

from pydantic import BaseModel, ConfigDict

from app.enums import Perfil


class UsuarioSaida(BaseModel):
    # from_attributes: permite montar o schema a partir de um objeto do banco
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    perfil: Perfil
    ativo: bool
