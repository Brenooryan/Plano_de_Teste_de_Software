"""Testes de sistema dos cabeçalhos de segurança (alertas do OWASP ZAP)."""

import pytest

from app.api.cabecalhos import CABECALHOS_DE_SEGURANCA


@pytest.mark.parametrize(
    ("rota", "status_esperado"),
    [
        ("/health", 200),            # resposta de sucesso
        ("/livros", 401),            # resposta de erro gerada pela API
        ("/rota-que-nao-existe", 404),  # resposta de erro gerada pelo framework
    ],
)
def test_toda_resposta_traz_os_cabecalhos_de_seguranca(cliente, rota, status_esperado):
    resposta = cliente.get(rota)

    assert resposta.status_code == status_esperado
    for nome, valor in CABECALHOS_DE_SEGURANCA.items():
        assert resposta.headers[nome] == valor
