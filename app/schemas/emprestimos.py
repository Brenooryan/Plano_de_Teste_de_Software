"""Formatos de entrada e saída de empréstimo, devolução e multa."""

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.config import MAIOR_ID

# Correção do DEF-02: todo identificador recebido tem faixa válida declarada.
# Fora dela, a própria validação responde 422, antes de chegar ao banco.
IdNoCorpo = Annotated[int, Field(ge=1, le=MAIOR_ID)]


class EmprestimoEntrada(BaseModel):
    exemplar_id: IdNoCorpo


class DevolucaoEntrada(BaseModel):
    exemplar_id: IdNoCorpo


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
