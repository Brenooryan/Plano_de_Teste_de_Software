"""Fonte da data atual (RNF11).

As regras que dependem de data nunca consultam o calendário diretamente:
elas recebem a data como parâmetro. Este é o único ponto do sistema que lê
o relógio, e nos testes ele é substituído por uma data fixa.
"""

from datetime import date


def data_atual() -> date:
    """Data de hoje, segundo o relógio do servidor."""
    return date.today()
