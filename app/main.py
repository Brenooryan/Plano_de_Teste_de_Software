"""Ponto de entrada da API: cria a aplicação e registra as rotas."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import acervo, auth, emprestimos, multas, usuarios
from app.api.erros import registrar_tratadores_de_erro
from app.dados_iniciais import criar_dados_iniciais
from app.database import Base, SessionLocal, engine


@asynccontextmanager
async def ao_iniciar(_app: FastAPI):
    """Executado uma vez na subida do servidor: cria tabelas e dados iniciais."""
    Base.metadata.create_all(engine)
    with SessionLocal() as sessao:
        criar_dados_iniciais(sessao)
    yield


app = FastAPI(
    title="API de Biblioteca",
    description="Sistema-alvo do Plano de Teste de Software (TS09).",
    version="1.0.0",
    lifespan=ao_iniciar,
)

registrar_tratadores_de_erro(app)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(acervo.router)
app.include_router(emprestimos.router)
app.include_router(multas.router)


@app.get("/health", tags=["Infraestrutura"])
def health() -> dict[str, str]:
    """Indica se a API está no ar."""
    return {"status": "ok"}
