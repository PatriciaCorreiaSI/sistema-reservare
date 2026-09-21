import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def criar(self, token: RefreshToken) -> RefreshToken:
        self._sessao.add(token)
        self._sessao.flush()
        return token

    def buscar_por_hash(self, hash_token: str) -> RefreshToken | None:
        consulta = select(RefreshToken).where(RefreshToken.hash_token == hash_token)
        return self._sessao.scalar(consulta)

    def revogar(self, token: RefreshToken, quando: datetime) -> RefreshToken:
        token.revogado_em = quando
        self._sessao.flush()
        return token

    def revogar_familia(self, familia_token: uuid.UUID, quando: datetime) -> None:
        comando = (
            update(RefreshToken)
            .where(RefreshToken.familia_token == familia_token)
            .where(RefreshToken.revogado_em.is_(None))
            .values(revogado_em=quando)
        )
        self._sessao.execute(comando)
        self._sessao.flush()
