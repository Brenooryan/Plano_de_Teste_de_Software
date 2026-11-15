"""Tabela de usuários (M1)."""

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import Perfil


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)  # RF03
    senha_hash: Mapped[str] = mapped_column(String(255))  # RNF02: nunca a senha pura
    perfil: Mapped[Perfil] = mapped_column(Enum(Perfil))
    ativo: Mapped[bool] = mapped_column(default=True)
