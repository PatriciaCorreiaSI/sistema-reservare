import os
import secrets
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Any

import jwt
from pwdlib import PasswordHash

ACCESS_MINUTOS = 15
REFRESH_DIAS = 7
JWT_ALGORITMO = "HS256"
JWT_SEGREDO = os.environ["JWT_SEGREDO"]

hasher = PasswordHash.recommended()


def criar_access_token(
    id_usuario: int, privilegio_usuario: str, agora: datetime
) -> str:
    payload = {
        "sub": str(id_usuario),
        "exp": agora + timedelta(minutes=ACCESS_MINUTOS),
        "privilegio_usuario": privilegio_usuario,
    }
    return jwt.encode(payload, JWT_SEGREDO, algorithm=JWT_ALGORITMO)


def gerar_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(refresh_token: str) -> str:
    return sha256(refresh_token.encode()).hexdigest()


def decodificar_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SEGREDO, algorithms=[JWT_ALGORITMO])
