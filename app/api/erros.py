"""Tradução dos erros de domínio em respostas HTTP (RNF06 e RNF07)."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.excecoes import NaoEncontradoError, RegraDeNegocioError


def registrar_tratadores_de_erro(app: FastAPI) -> None:
    @app.exception_handler(NaoEncontradoError)
    async def recurso_inexistente(_requisicao: Request, erro: NaoEncontradoError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": erro.mensagem},
        )

    @app.exception_handler(RegraDeNegocioError)
    async def regra_violada(_requisicao: Request, erro: RegraDeNegocioError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": erro.mensagem, "codigo": erro.codigo},
        )
