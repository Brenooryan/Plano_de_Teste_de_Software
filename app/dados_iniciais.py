"""Dados criados na primeira execução, para o sistema ser utilizável.

ATENÇÃO: as senhas abaixo são de demonstração. Em um sistema real, nenhuma
credencial ficaria no código-fonte.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import Perfil
from app.models import Exemplar, Livro, Usuario
from app.seguranca import gerar_hash_senha

EMAIL_BIBLIOTECARIO = "bibliotecario@biblioteca.local"
SENHA_BIBLIOTECARIO = "biblio1234"
EMAIL_ALUNO = "aluno@biblioteca.local"
SENHA_ALUNO = "aluno1234"
EMAIL_PROFESSOR = "professor@biblioteca.local"
SENHA_PROFESSOR = "professor1234"

EXEMPLARES_POR_LIVRO = 2
LIVROS = [
    ("Dom Casmurro", "Machado de Assis", "9788535902778"),
    ("Grande Sertão: Veredas", "João Guimarães Rosa", "9788535908831"),
    ("Vidas Secas", "Graciliano Ramos", "9788501114785"),
    ("A Hora da Estrela", "Clarice Lispector", "9788532508126"),
    ("Capitães da Areia", "Jorge Amado", "9788535914061"),
]


def criar_dados_iniciais(sessao: Session) -> None:
    """Cria usuários e acervo, apenas se o banco ainda estiver vazio."""
    if sessao.scalars(select(Usuario.id).limit(1)).first() is not None:
        return

    sessao.add_all(
        [
            Usuario(
                nome="Bibliotecário",
                email=EMAIL_BIBLIOTECARIO,
                senha_hash=gerar_hash_senha(SENHA_BIBLIOTECARIO),
                perfil=Perfil.BIBLIOTECARIO,
            ),
            Usuario(
                nome="Aluno de Demonstração",
                email=EMAIL_ALUNO,
                senha_hash=gerar_hash_senha(SENHA_ALUNO),
                perfil=Perfil.ALUNO,
            ),
            Usuario(
                nome="Professor de Demonstração",
                email=EMAIL_PROFESSOR,
                senha_hash=gerar_hash_senha(SENHA_PROFESSOR),
                perfil=Perfil.PROFESSOR,
            ),
        ]
    )

    for titulo, autor, isbn in LIVROS:
        livro = Livro(titulo=titulo, autor=autor, isbn=isbn)
        sessao.add(livro)
        sessao.add_all([Exemplar(livro=livro) for _ in range(EXEMPLARES_POR_LIVRO)])

    sessao.commit()
