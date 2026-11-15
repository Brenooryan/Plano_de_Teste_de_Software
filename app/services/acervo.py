"""Casos de uso do acervo: consulta de livros e exemplares."""

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Exemplar, Livro


def listar_acervo(sessao: Session) -> list[tuple[Livro, list[Exemplar]]]:
    """Devolve cada livro acompanhado da lista dos seus exemplares."""
    livros = sessao.scalars(select(Livro).order_by(Livro.titulo)).all()
    exemplares = sessao.scalars(select(Exemplar).order_by(Exemplar.id)).all()

    exemplares_por_livro: dict[int, list[Exemplar]] = defaultdict(list)
    for exemplar in exemplares:
        exemplares_por_livro[exemplar.livro_id].append(exemplar)

    return [(livro, exemplares_por_livro[livro.id]) for livro in livros]
