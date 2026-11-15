"""Casos de uso de usuário: autenticação (RF04 e RF05)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Usuario
from app.seguranca import gerar_hash_senha, verificar_senha

# Usado quando o e-mail não existe, para que a resposta demore o mesmo
# tempo de uma senha errada. Sem isso, o tempo de resposta revelaria
# quais e-mails estão cadastrados.
_HASH_DE_COMPARACAO = gerar_hash_senha("valor-usado-apenas-para-igualar-o-tempo")


def autenticar(sessao: Session, email: str, senha: str) -> Usuario | None:
    """Devolve o usuário se e-mail e senha conferem; caso contrário, None."""
    usuario = sessao.scalars(select(Usuario).where(Usuario.email == email)).first()

    if usuario is None:
        verificar_senha(senha, _HASH_DE_COMPARACAO)
        return None

    if not verificar_senha(senha, usuario.senha_hash):
        return None

    return usuario
