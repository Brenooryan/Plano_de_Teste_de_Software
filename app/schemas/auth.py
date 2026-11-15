"""Formatos de entrada e saída do login."""

from pydantic import BaseModel


class LoginEntrada(BaseModel):
    email: str
    senha: str


class TokenSaida(BaseModel):
    access_token: str
    # "bearer" é o nome do tipo de token, não uma senha: falso positivo da regra S105
    token_type: str = "bearer"  # noqa: S105
