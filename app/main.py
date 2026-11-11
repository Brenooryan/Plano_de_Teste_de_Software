"""Ponto de entrada da API: cria a aplicação e registra as rotas."""

from fastapi import FastAPI

app = FastAPI(
    title="API de Biblioteca",
    description="Sistema-alvo do Plano de Teste de Software (TS09).",
    version="0.1.0",
)


@app.get("/health", tags=["Infraestrutura"])
def health() -> dict[str, str]:
    """Indica se a API está no ar."""
    return {"status": "ok"}
