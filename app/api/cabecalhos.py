"""Cabeçalhos de segurança incluídos em todas as respostas.

Correção dos dois alertas de risco baixo apontados pelo OWASP ZAP
(categoria "configuração de segurança incorreta" do OWASP Top 10).
"""

from fastapi import FastAPI, Request

CABECALHOS_DE_SEGURANCA = {
    # Impede o navegador de "adivinhar" o tipo do conteúdo da resposta
    "X-Content-Type-Options": "nosniff",
    # Impede que páginas de outros sites carreguem as respostas desta API
    "Cross-Origin-Resource-Policy": "same-origin",
}


def registrar_cabecalhos_de_seguranca(app: FastAPI) -> None:
    # Um middleware roda em volta de TODAS as requisições, inclusive as que
    # terminam em erro. Por isso os cabeçalhos valem também para 401, 404 etc.
    @app.middleware("http")
    async def adicionar_cabecalhos(requisicao: Request, chamar_proximo):
        resposta = await chamar_proximo(requisicao)
        for nome, valor in CABECALHOS_DE_SEGURANCA.items():
            resposta.headers[nome] = valor
        return resposta
