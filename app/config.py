"""Parâmetros do sistema (seção 3 de docs/requisitos.md).

Todos os números das regras de negócio ficam aqui. Se uma regra mudar,
a alteração é feita em um único lugar.
"""

from decimal import Decimal

# --- Multa (RF22) ---
MULTA_POR_DIA = Decimal("1.00")
TETO_MULTA = Decimal("30.00")
