"""Modelos: as tabelas do banco de dados descritas como classes Python.

Importar este pacote registra todas as tabelas na Base.
"""

from app.models.acervo import Exemplar, Livro
from app.models.emprestimos import Emprestimo
from app.models.multas import Multa
from app.models.usuarios import Usuario

__all__ = ["Emprestimo", "Exemplar", "Livro", "Multa", "Usuario"]
