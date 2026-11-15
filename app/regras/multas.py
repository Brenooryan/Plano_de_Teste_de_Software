"""Regras de atraso e multa (RF21 e RF22)."""

from datetime import date
from decimal import Decimal

from app.config import MULTA_POR_DIA, TETO_MULTA


def calcular_dias_atraso(data_prevista: date, data_devolucao: date) -> int:
    """RF21: dias corridos entre a data prevista e a devolução.

    Devolução no prazo ou adiantada resulta em 0 (nunca em valor negativo).
    """
    diferenca = (data_devolucao - data_prevista).days
    return max(diferenca, 0)


def calcular_multa(dias_atraso: int) -> Decimal:
    """RF22: R$ 1,00 por dia de atraso, limitada ao teto por empréstimo."""
    if dias_atraso < 0:
        raise ValueError("dias_atraso não pode ser negativo")

    multa = MULTA_POR_DIA * dias_atraso
    return min(multa, TETO_MULTA)
