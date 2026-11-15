"""Regras de empréstimo (RF14, RF15, RF16 e RF18)."""

from datetime import date, timedelta
from enum import Enum

from app.config import LIMITE_EMPRESTIMOS, PRAZO_EMPRESTIMO_DIAS
from app.enums import EstadoExemplar, Perfil


class MotivoRecusa(str, Enum):
    """Condição não atendida em um pedido de empréstimo (RF14)."""

    PERFIL_NAO_PERMITIDO = "perfil_nao_permitido"
    CONTA_INATIVA = "conta_inativa"
    MULTA_PENDENTE = "multa_pendente"
    LIMITE_ATINGIDO = "limite_atingido"
    EXEMPLAR_INDISPONIVEL = "exemplar_indisponivel"


def verificar_emprestimo(
    perfil: Perfil,
    conta_ativa: bool,
    tem_multa_pendente: bool,
    emprestimos_ativos: int,
    estado_exemplar: EstadoExemplar,
) -> MotivoRecusa | None:
    """Decide se o empréstimo pode ser feito.

    Retorna None quando todas as condições são atendidas. Caso contrário,
    retorna o primeiro motivo de recusa, na ordem de verificação abaixo.
    """
    # RF18: bibliotecário é perfil administrativo e não empresta
    if perfil not in LIMITE_EMPRESTIMOS:
        return MotivoRecusa.PERFIL_NAO_PERMITIDO

    # RF14 (a): conta ativa
    if not conta_ativa:
        return MotivoRecusa.CONTA_INATIVA

    # RF14 (b): nenhuma multa pendente
    if tem_multa_pendente:
        return MotivoRecusa.MULTA_PENDENTE

    # RF14 (c) e RF15: abaixo do limite do perfil
    if emprestimos_ativos >= LIMITE_EMPRESTIMOS[perfil]:
        return MotivoRecusa.LIMITE_ATINGIDO

    # RF14 (d): exemplar disponível
    if estado_exemplar != EstadoExemplar.DISPONIVEL:
        return MotivoRecusa.EXEMPLAR_INDISPONIVEL

    return None


def calcular_data_prevista(perfil: Perfil, data_emprestimo: date) -> date:
    """RF16: data do empréstimo somada ao prazo do perfil, em dias corridos."""
    if perfil not in PRAZO_EMPRESTIMO_DIAS:
        raise ValueError(f"perfil sem prazo de empréstimo: {perfil.value}")

    return data_emprestimo + timedelta(days=PRAZO_EMPRESTIMO_DIAS[perfil])
