"""Rotas de multa (M4)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencias import (
    IdNoCaminho,
    apenas_bibliotecario,
    obter_sessao,
    proprio_usuario_ou_bibliotecario,
)
from app.schemas.emprestimos import MultaSaida
from app.services.multas import listar_multas_do_usuario, pagar_multa

router = APIRouter(tags=["Multas"])


@router.get(
    "/usuarios/{usuario_id}/multas",
    response_model=list[MultaSaida],
    dependencies=[Depends(proprio_usuario_ou_bibliotecario)],
)
def listar_multas(
    usuario_id: IdNoCaminho, sessao: Session = Depends(obter_sessao)
) -> list[MultaSaida]:
    """Multas de um usuário: só ele mesmo ou o bibliotecário podem ver."""
    return [MultaSaida.model_validate(m) for m in listar_multas_do_usuario(sessao, usuario_id)]


@router.post(
    "/multas/{multa_id}/pagamento",
    response_model=MultaSaida,
    dependencies=[Depends(apenas_bibliotecario)],
)
def registrar_pagamento(
    multa_id: IdNoCaminho, sessao: Session = Depends(obter_sessao)
) -> MultaSaida:
    """O bibliotecário registra o pagamento integral da multa."""
    return MultaSaida.model_validate(pagar_multa(sessao, multa_id))
