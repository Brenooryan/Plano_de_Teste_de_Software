"""Tabela de multas (M4)."""

from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.emprestimos import Emprestimo
from app.models.usuarios import Usuario


class Multa(Base):
    __tablename__ = "multas"

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique=True: no máximo uma multa por empréstimo
    emprestimo_id: Mapped[int] = mapped_column(ForeignKey("emprestimos.id"), unique=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    # Dinheiro guardado em centavos (inteiro): o SQLite não tem tipo decimal exato
    valor_centavos: Mapped[int]
    paga: Mapped[bool] = mapped_column(default=False)

    emprestimo: Mapped[Emprestimo] = relationship()
    usuario: Mapped[Usuario] = relationship()

    @property
    def valor(self) -> Decimal:
        """Valor em reais, convertido a partir dos centavos."""
        return (Decimal(self.valor_centavos) / 100).quantize(Decimal("0.01"))
