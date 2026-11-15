"""Erros de domínio.

Os serviços lançam estes erros sem saber nada de HTTP. A camada de API é
quem os traduz em códigos de resposta (404, 409).
"""


class ErroDeDominio(Exception):
    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem


class NaoEncontradoError(ErroDeDominio):
    """O recurso pedido não existe."""


class RegraDeNegocioError(ErroDeDominio):
    """A operação viola uma regra de negócio ou uma transição de estado."""

    def __init__(self, codigo: str, mensagem: str):
        super().__init__(mensagem)
        self.codigo = codigo
