"""Tabela de empréstimos (M3)."""

from datetime import date
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.acervo import Exemplar
from app.models.usuarios import Usuario


class Emprestimo(Base):
    __tablename__ = "emprestimos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    exemplar_id: Mapped[int] = mapped_column(ForeignKey("exemplares.id"))
    data_emprestimo: Mapped[date]
    data_prevista: Mapped[date]
    data_devolucao: Mapped[Optional[date]] = mapped_column(default=None)

    usuario: Mapped[Usuario] = relationship()
    exemplar: Mapped[Exemplar] = relationship()

    @property
    def ativo(self) -> bool:
        """Empréstimo ativo é o que ainda não foi devolvido."""
        return self.data_devolucao is None
