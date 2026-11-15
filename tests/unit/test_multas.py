"""Testes unitários das regras de atraso e multa (RF21 e RF22).

Técnicas: partição de equivalência e análise do valor limite.
"""

from datetime import date
from decimal import Decimal

import pytest

from app.regras.multas import calcular_dias_atraso, calcular_multa

DATA_PREVISTA = date(2026, 11, 10)


# --- RF21: dias de atraso -------------------------------------------------
# Partições: devolução antes do prazo | no prazo | depois do prazo
# Limite: a própria data prevista (um dia antes, no dia, um dia depois)


@pytest.mark.parametrize(
    ("data_devolucao", "dias_esperados"),
    [
        (date(2026, 11, 9), 0),    # um dia antes do prazo
        (date(2026, 11, 10), 0),   # exatamente no prazo (limite)
        (date(2026, 11, 11), 1),   # um dia depois do prazo (limite)
        (date(2026, 12, 10), 30),  # atraso que atravessa a virada do mês
    ],
)
def test_dias_atraso(data_devolucao, dias_esperados):
    assert calcular_dias_atraso(DATA_PREVISTA, data_devolucao) == dias_esperados


# --- RF22: valor da multa -------------------------------------------------
# Partições: sem atraso (0) | proporcional (1 a 30) | no teto (acima de 30)
# Limites: 0/1 (início da cobrança) e 29/30/31 (teto de R$ 30,00)


@pytest.mark.parametrize(
    ("dias_atraso", "multa_esperada"),
    [
        (0, Decimal("0.00")),     # limite: sem atraso, sem multa
        (1, Decimal("1.00")),     # limite: primeiro dia cobrado
        (15, Decimal("15.00")),   # valor típico da partição proporcional
        (29, Decimal("29.00")),   # limite: um abaixo do teto
        (30, Decimal("30.00")),   # limite: exatamente no teto
        (31, Decimal("30.00")),   # limite: um acima do teto
        (365, Decimal("30.00")),  # valor típico da partição "no teto"
    ],
)
def test_valor_da_multa(dias_atraso, multa_esperada):
    assert calcular_multa(dias_atraso) == multa_esperada


def test_multa_recusa_dias_negativos():
    # Partição inválida: a função não aceita atraso negativo
    with pytest.raises(ValueError):
        calcular_multa(-1)
