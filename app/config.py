"""Parâmetros do sistema (seção 3 de docs/requisitos.md).

Todos os números das regras de negócio ficam aqui. Se uma regra mudar,
a alteração é feita em um único lugar.
"""

import os
from decimal import Decimal

from app.enums import Perfil

# --- Autenticação (RF04) ---
VALIDADE_TOKEN_MINUTOS = 30
# Chave que assina os tokens. Em produção, vem da variável de ambiente;
# o valor padrão existe apenas para desenvolvimento e testes.
CHAVE_SECRETA = os.environ.get(
    "BIBLIOTECA_CHAVE_SECRETA", "chave-de-desenvolvimento-nao-usar-em-producao"
)

# --- Identificadores (RNF07) ---
# Maior inteiro que o SQLite armazena. Um id acima disso é entrada inválida.
MAIOR_ID = 2**63 - 1

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
