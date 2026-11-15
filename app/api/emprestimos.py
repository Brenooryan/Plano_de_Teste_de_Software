"""Rotas de empréstimo e devolução (M3 e M4)."""

from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencias import (
    IdNoCaminho,
    apenas_bibliotecario,
    apenas_leitores,
    obter_data_atual,
    obter_sessao,
    proprio_usuario_ou_bibliotecario,
)
from app.models import Usuario
from app.schemas.emprestimos import (
    DevolucaoEntrada,
    DevolucaoSaida,
    EmprestimoEntrada,
    EmprestimoSaida,
    MultaSaida,
)
from app.services.emprestimos import devolver, emprestar, listar_emprestimos_do_usuario

router = APIRouter(tags=["Empréstimos"])


@router.post("/emprestimos", response_model=EmprestimoSaida, status_code=status.HTTP_201_CREATED)
def criar_emprestimo(
    dados: EmprestimoEntrada,
    sessao: Session = Depends(obter_sessao),
    hoje: date = Depends(obter_data_atual),
    usuario: Usuario = Depends(apenas_leitores),
) -> EmprestimoSaida:
    """O usuário do token (aluno ou professor) empresta um exemplar."""
    emprestimo = emprestar(sessao, usuario.id, dados.exemplar_id, hoje)
    return EmprestimoSaida.model_validate(emprestimo)


@router.post(
    "/devolucoes",
    response_model=DevolucaoSaida,
    dependencies=[Depends(apenas_bibliotecario)],
)
def registrar_devolucao(
    dados: DevolucaoEntrada,
    sessao: Session = Depends(obter_sessao),
    hoje: date = Depends(obter_data_atual),
) -> DevolucaoSaida:
    """O bibliotecário registra a devolução. Atraso gera multa."""
    emprestimo, multa = devolver(sessao, dados.exemplar_id, hoje)
    return DevolucaoSaida(
        emprestimo=EmprestimoSaida.model_validate(emprestimo),
        multa=MultaSaida.model_validate(multa) if multa is not None else None,
    )


@router.get(
    "/usuarios/{usuario_id}/emprestimos",
    response_model=list[EmprestimoSaida],
    dependencies=[Depends(proprio_usuario_ou_bibliotecario)],
)
def listar_emprestimos(
    usuario_id: IdNoCaminho, sessao: Session = Depends(obter_sessao)
) -> list[EmprestimoSaida]:
    """Empréstimos de um usuário: só ele mesmo ou o bibliotecário podem ver."""
    emprestimos = listar_emprestimos_do_usuario(sessao, usuario_id)
    return [EmprestimoSaida.model_validate(e) for e in emprestimos]
