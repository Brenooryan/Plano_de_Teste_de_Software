"""Formatos de entrada e saída do login."""

from pydantic import BaseModel


class LoginEntrada(BaseModel):
    email: str
    senha: str


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"
