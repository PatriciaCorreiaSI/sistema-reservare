import uuid
from datetime import UTC, datetime

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import obter_sessao
from app.models import Usuario
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.usuario import UsuarioRepository
from app.schemas.auth import LoginEntrada, RefreshEntrada, TokenResposta
from app.security import (
    hash_refresh_token,
    hasher,
)
from app.services.excecoes import CredenciaisInvalidas


class AuthService:
    def __init__(self, sessao: Session = Depends(obter_sessao)) -> None:
        self._sessao = sessao
        self._refresh_tokens = RefreshTokenRepository(sessao)
        self._usuarios = UsuarioRepository(sessao)

    def login(self, dados: LoginEntrada) -> TokenResposta:
        agora = datetime.now(UTC)
        usuario = self._usuarios.buscar_por_email(dados.email_usuario)
        if (
            usuario is None
            or usuario.status_usuario != "ativo"
            or not hasher.verify(dados.senha, usuario.senha_usuario_hash)
        ):
            raise CredenciaisInvalidas()
        return self._emitir_tokens(usuario, uuid.uuid4(), agora)

    def renovar(self, dados: RefreshEntrada) -> TokenResposta:
        agora = datetime.now(UTC)
        hash_token = hash_refresh_token(dados.refresh_token)
        token = self._refresh_tokens.buscar_por_hash(hash_token)
        if token is None:
            raise CredenciaisInvalidas()
        if token.revogado_em is not None:
            self._refresh_tokens.revogar_familia(token.familia_token, agora)
            # Emenda ao ADR 0010: a revogação precisa sobreviver ao rollback do 401.
            self._sessao.commit()
            raise CredenciaisInvalidas()
        if token.expira_em < agora:
            raise CredenciaisInvalidas()
        usuario = self._usuarios.buscar_por_id(token.id_usuario)
        if usuario is None or usuario.status_usuario != "ativo":
            raise CredenciaisInvalidas()
        self._refresh_tokens.revogar(token, agora)
        return self._emitir_tokens(usuario, token.familia_token, agora)

    def logout(self, dados: RefreshEntrada) -> None:
        raise NotImplementedError

    def _emitir_tokens(
        self, usuario: Usuario, familia_token: uuid.UUID, agora: datetime
    ) -> TokenResposta:
        raise NotImplementedError
