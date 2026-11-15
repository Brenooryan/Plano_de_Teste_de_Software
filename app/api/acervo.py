"""Rotas do acervo (M2)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencias import obter_sessao, obter_usuario_atual
from app.enums import EstadoExemplar
from app.schemas.acervo import ExemplarSaida, LivroSaida
from app.services.acervo import listar_acervo

router = APIRouter(prefix="/livros", tags=["Acervo"])


@router.get("", response_model=list[LivroSaida], dependencies=[Depends(obter_usuario_atual)])
def listar_livros(sessao: Session = Depends(obter_sessao)) -> list[LivroSaida]:
    """Lista os livros com seus exemplares. Exige usuário autenticado."""
    return [
        LivroSaida(
            id=livro.id,
            titulo=livro.titulo,
            autor=livro.autor,
            isbn=livro.isbn,
            disponiveis=sum(1 for e in exemplares if e.estado == EstadoExemplar.DISPONIVEL),
            exemplares=[ExemplarSaida(id=e.id, estado=e.estado) for e in exemplares],
        )
        for livro, exemplares in listar_acervo(sessao)
    ]
