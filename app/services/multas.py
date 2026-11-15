"""Casos de uso de multa (RF23 e RF24)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.excecoes import NaoEncontradoError, RegraDeNegocioError
from app.models import Multa


def tem_multa_pendente(sessao: Session, usuario_id: int) -> bool:
    """RF23: o usuário está bloqueado enquanto tiver alguma multa não paga."""
    consulta = (
        select(Multa.id)
        .where(Multa.usuario_id == usuario_id, Multa.paga.is_(False))
        .limit(1)
    )
    return sessao.scalars(consulta).first() is not None


def pagar_multa(sessao: Session, multa_id: int) -> Multa:
    """RF24: registra o pagamento integral de uma multa."""
    multa = sessao.get(Multa, multa_id)
    if multa is None:
        raise NaoEncontradoError("Multa não encontrada")

    if multa.paga:
        raise RegraDeNegocioError("multa_ja_paga", "Multa já está paga")

    multa.paga = True
    sessao.commit()
    return multa
