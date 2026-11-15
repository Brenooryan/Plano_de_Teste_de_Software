"""Parâmetros do sistema (seção 3 de docs/requisitos.md).

Todos os números das regras de negócio ficam aqui. Se uma regra mudar,
a alteração é feita em um único lugar.
"""

from decimal import Decimal

from app.enums import Perfil

# --- Empréstimo (RF15 e RF16) ---
LIMITE_EMPRESTIMOS = {
    Perfil.ALUNO: 3,
    Perfil.PROFESSOR: 5,
}
PRAZO_EMPRESTIMO_DIAS = {
    Perfil.ALUNO: 7,
    Perfil.PROFESSOR: 14,
}

# --- Multa (RF22) ---
MULTA_POR_DIA = Decimal("1.00")
TETO_MULTA = Decimal("30.00")
