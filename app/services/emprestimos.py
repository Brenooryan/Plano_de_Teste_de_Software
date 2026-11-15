"""Casos de uso de empréstimo e devolução (RF14 a RF22)."""

from datetime import date

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.config import LIMITE_EMPRESTIMOS
from app.enums import EstadoExemplar, Perfil
from app.excecoes import NaoEncontradoError, RegraDeNegocioError
from app.models import Emprestimo, Exemplar, Multa, Usuario
from app.regras.emprestimos import (
    MotivoRecusa,
    calcular_data_prevista,
    verificar_emprestimo,
)
from app.regras.multas import calcular_dias_atraso, calcular_multa
from app.services.multas import tem_multa_pendente

_MENSAGENS_DE_RECUSA = {
    MotivoRecusa.PERFIL_NAO_PERMITIDO: "Bibliotecários não podem realizar empréstimos",
    MotivoRecusa.CONTA_INATIVA: "Conta inativa",
    MotivoRecusa.MULTA_PENDENTE: "Usuário com multa pendente",
    MotivoRecusa.EXEMPLAR_INDISPONIVEL: "Exemplar não está disponível",
}


def _mensagem_de_recusa(motivo: MotivoRecusa, perfil: Perfil) -> str:
    """RNF06: mensagem em português que explica o motivo da recusa."""
    if motivo == MotivoRecusa.LIMITE_ATINGIDO:
        return f"Limite de {LIMITE_EMPRESTIMOS[perfil]} empréstimos ativos atingido"
    return _MENSAGENS_DE_RECUSA[motivo]


def contar_emprestimos_ativos(sessao: Session, usuario_id: int) -> int:
    consulta = (
        select(func.count())
        .select_from(Emprestimo)
        .where(Emprestimo.usuario_id == usuario_id, Emprestimo.data_devolucao.is_(None))
    )
    return sessao.scalar(consulta) or 0


def listar_emprestimos_do_usuario(sessao: Session, usuario_id: int) -> list[Emprestimo]:
    if sessao.get(Usuario, usuario_id) is None:
        raise NaoEncontradoError("Usuário não encontrado")

    consulta = select(Emprestimo).where(Emprestimo.usuario_id == usuario_id).order_by(Emprestimo.id)
    return list(sessao.scalars(consulta))


def emprestar(sessao: Session, usuario_id: int, exemplar_id: int, hoje: date) -> Emprestimo:
    """Registra um empréstimo, se todas as condições do RF14 forem atendidas."""
    try:
        # Correção do DEF-01 (condição de corrida): pega a trava de escrita do
        # banco ANTES de ler qualquer dado. Um pedido simultâneo fica esperando
        # nesta linha e, quando entra, já lê o estado deixado pelo anterior.
        sessao.execute(text("BEGIN IMMEDIATE"))

        emprestimo = _registrar_emprestimo(sessao, usuario_id, exemplar_id, hoje)

        sessao.commit()  # grava tudo e libera a trava
        return emprestimo
    except Exception:
        sessao.rollback()  # desfaz tudo e libera a trava
        raise


def _registrar_emprestimo(
    sessao: Session, usuario_id: int, exemplar_id: int, hoje: date
) -> Emprestimo:
    """Lê, decide e prepara a gravação. Deve rodar dentro da trava de escrita."""
    # 1. Busca os dados
    usuario = sessao.get(Usuario, usuario_id)
    if usuario is None:
        raise NaoEncontradoError("Usuário não encontrado")

    # populate_existing: relê o exemplar do banco mesmo que a sessão já o conheça
    exemplar = sessao.get(Exemplar, exemplar_id, populate_existing=True)
    if exemplar is None:
        raise NaoEncontradoError("Exemplar não encontrado")

    # 2. Aplica a regra pura
    motivo = verificar_emprestimo(
        perfil=usuario.perfil,
        conta_ativa=usuario.ativo,
        tem_multa_pendente=tem_multa_pendente(sessao, usuario.id),
        emprestimos_ativos=contar_emprestimos_ativos(sessao, usuario.id),
        estado_exemplar=exemplar.estado,
    )
    if motivo is not None:
        raise RegraDeNegocioError(motivo.value, _mensagem_de_recusa(motivo, usuario.perfil))

    # 3. Prepara a gravação; o commit é feito por quem pegou a trava (RNF05)
    emprestimo = Emprestimo(
        usuario=usuario,
        exemplar=exemplar,
        data_emprestimo=hoje,
        data_prevista=calcular_data_prevista(usuario.perfil, hoje),
    )
    exemplar.estado = EstadoExemplar.EMPRESTADO  # RF17
    sessao.add(emprestimo)
    return emprestimo


def devolver(sessao: Session, exemplar_id: int, hoje: date) -> tuple[Emprestimo, Multa | None]:
    """Registra a devolução. Retorna o empréstimo encerrado e a multa, se houver."""
    exemplar = sessao.get(Exemplar, exemplar_id)
    if exemplar is None:
        raise NaoEncontradoError("Exemplar não encontrado")

    # RF20: transição inválida
    if exemplar.estado != EstadoExemplar.EMPRESTADO:
        raise RegraDeNegocioError("exemplar_nao_emprestado", "Exemplar não está emprestado")

    emprestimo = sessao.scalars(
        select(Emprestimo).where(
            Emprestimo.exemplar_id == exemplar.id,
            Emprestimo.data_devolucao.is_(None),
        )
    ).one()

    # RF19: encerra o empréstimo e libera o exemplar
    emprestimo.data_devolucao = hoje
    exemplar.estado = EstadoExemplar.DISPONIVEL

    # RF21 e RF22: atraso gera multa
    multa = None
    dias_atraso = calcular_dias_atraso(emprestimo.data_prevista, hoje)
    if dias_atraso > 0:
        valor = calcular_multa(dias_atraso)
        multa = Multa(
            emprestimo=emprestimo,
            usuario=emprestimo.usuario,
            valor_centavos=int(valor * 100),  # reais -> centavos
        )
        sessao.add(multa)

    sessao.commit()
    return emprestimo, multa
