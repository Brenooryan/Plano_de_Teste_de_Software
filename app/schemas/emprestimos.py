"""Formatos de entrada e saída de empréstimo, devolução e multa."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class EmprestimoEntrada(BaseModel):
    exemplar_id: int


class DevolucaoEntrada(BaseModel):
    exemplar_id: int


class EmprestimoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    exemplar_id: int
    data_emprestimo: date
    data_prevista: date
    data_devolucao: date | None


class MultaSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    emprestimo_id: int
    usuario_id: int
    valor: Decimal  # no JSON, sai como texto ("3.00") para não perder precisão
    paga: bool


class DevolucaoSaida(BaseModel):
    emprestimo: EmprestimoSaida
    multa: MultaSaida | None
