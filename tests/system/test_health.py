"""Teste de fumaça: verifica se a API sobe e responde."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_retorna_200_e_status_ok():
    # Arrange: nada a preparar — a API não tem estado nesta etapa

    # Act
    resposta = client.get("/health")

    # Assert
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}
