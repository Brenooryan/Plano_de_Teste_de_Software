"""Tabelas do acervo (M2): livros e exemplares."""

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import EstadoExemplar


class Livro(Base):
    """A obra. Um livro pode ter vários exemplares."""

    __tablename__ = "livros"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    autor: Mapped[str] = mapped_column(String(200))
    isbn: Mapped[str] = mapped_column(String(13), unique=True)  # RF10


class Exemplar(Base):
    """Cada cópia física de um livro. É o exemplar que é emprestado."""

    __tablename__ = "exemplares"

    id: Mapped[int] = mapped_column(primary_key=True)
    livro_id: Mapped[int] = mapped_column(ForeignKey("livros.id"))
    estado: Mapped[EstadoExemplar] = mapped_column(
        Enum(EstadoExemplar), default=EstadoExemplar.DISPONIVEL  # RF11
    )

    livro: Mapped[Livro] = relationship()
