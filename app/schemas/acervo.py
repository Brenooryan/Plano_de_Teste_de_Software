"""Formatos de saída do acervo."""

from pydantic import BaseModel

from app.enums import EstadoExemplar


class ExemplarSaida(BaseModel):
    id: int
    estado: EstadoExemplar


class LivroSaida(BaseModel):
    id: int
    titulo: str
    autor: str
    isbn: str
    disponiveis: int
    exemplares: list[ExemplarSaida]
