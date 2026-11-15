"""Enumerações do domínio, compartilhadas entre as camadas.

Ficam fora de app/regras e de app/models para que as regras não precisem
importar nada da camada de banco de dados.
"""

from enum import Enum


class Perfil(str, Enum):
    ALUNO = "aluno"
    PROFESSOR = "professor"
    BIBLIOTECARIO = "bibliotecario"


class EstadoExemplar(str, Enum):
    DISPONIVEL = "disponivel"
    EMPRESTADO = "emprestado"
