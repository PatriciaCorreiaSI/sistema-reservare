from datetime import UTC, datetime

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.security import decodificar_access_token
from app.services.excecoes import CredenciaisInvalidas, PrivilegioInsuficiente


class UsuarioAtual(BaseModel):
    id_usuario: int
    privilegio_usuario: str


def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> UsuarioAtual:
    try:
        payload = decodificar_access_token(credenciais.credentials)
    except jwt.InvalidTokenError as erro:
        raise CredenciaisInvalidas from erro
    return UsuarioAtual(
        id_usuario=int(payload["sub"]),
        privilegio_usuario=payload["privilegio_usuario"],
    )


def exigir_admin(usuario: UsuarioAtual = Depends(obter_usuario_atual)) -> UsuarioAtual:
    if usuario.privilegio_usuario != "admin":
        raise PrivilegioInsuficiente
    return usuario


def obter_agora() -> datetime:
    return datetime.now(UTC)
