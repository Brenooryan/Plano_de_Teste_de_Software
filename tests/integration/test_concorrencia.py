"""Teste de regressão do defeito DEF-01 (RNF05 e RF15).

Reproduz, sem depender do k6, a disputa de vários pedidos simultâneos pelo
mesmo exemplar. Cada pedido roda em uma thread, com a sua própria sessão e a
sua própria conexão com o banco, como acontece com requisições reais na API.
"""

import threading
from datetime import date

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base
from app.enums import Perfil
from app.excecoes import RegraDeNegocioError
from app.models import Exemplar, Livro, Usuario
from app.services.emprestimos import contar_emprestimos_ativos, emprestar

HOJE = date(2026, 11, 10)
PEDIDOS_SIMULTANEOS = 20


@pytest.fixture
def fabrica_de_sessoes(tmp_path):
    """Sessões sobre um banco em ARQUIVO, com uma conexão nova para cada sessão.

    O banco em memória dos outros testes usa uma conexão única, compartilhada.
    Com uma conexão só não existe disputa, e o defeito nunca apareceria.
    """
    caminho = (tmp_path / "concorrencia.db").as_posix()
    banco = create_engine(
        f"sqlite:///{caminho}",
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )
    Base.metadata.create_all(banco)

    yield sessionmaker(bind=banco)

    banco.dispose()


# O defeito não é determinístico: uma rodada isolada pode passar por sorte.
# Por isso o cenário é repetido em três rodadas independentes.
@pytest.mark.parametrize("rodada", [1, 2, 3])
def test_pedidos_simultaneos_pelo_mesmo_exemplar_geram_um_unico_emprestimo(
    fabrica_de_sessoes, rodada
):
    # Arrange: um aluno e um exemplar disponível
    with fabrica_de_sessoes() as sessao:
        aluno = Usuario(
            nome="Ana Aluna",
            email="ana@exemplo.com",
            senha_hash="hash-de-teste",
            perfil=Perfil.ALUNO,
        )
        livro = Livro(titulo="Dom Casmurro", autor="Machado de Assis", isbn="9788535902778")
        exemplar = Exemplar(livro=livro)
        sessao.add_all([aluno, exemplar])
        sessao.commit()
        aluno_id, exemplar_id = aluno.id, exemplar.id

    largada = threading.Barrier(PEDIDOS_SIMULTANEOS, timeout=30)
    resultados: list[str] = []

    def pedir_emprestimo() -> None:
        try:
            with fabrica_de_sessoes() as sessao:
                sessao.execute(text("SELECT 1"))  # abre a conexão antes da largada
                largada.wait()  # todas as threads partem juntas
                emprestar(sessao, aluno_id, exemplar_id, HOJE)
            resultados.append("aceito")
        except RegraDeNegocioError as erro:
            resultados.append(erro.codigo)
        except Exception as erro:  # qualquer outra falha reprova o teste
            resultados.append(f"erro inesperado: {erro!r}")

    # Act: 20 pedidos ao mesmo tempo
    threads = [threading.Thread(target=pedir_emprestimo) for _ in range(PEDIDOS_SIMULTANEOS)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Assert: um aceito, os demais recusados, e um único empréstimo gravado
    with fabrica_de_sessoes() as sessao:
        ativos_no_banco = contar_emprestimos_ativos(sessao, aluno_id)

    assert resultados.count("aceito") == 1, resultados
    assert resultados.count("exemplar_indisponivel") == PEDIDOS_SIMULTANEOS - 1, resultados
    assert ativos_no_banco == 1
