from typing import Literal

from pydantic import BaseModel, ConfigDict


class UsuarioCriar(BaseModel):
    nome_usuario: str
    email_usuario: str
    senha: str
    privilegio_usuario: Literal["admin", "usuario"]


class UsuarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    nome_usuario: str
    email_usuario: str
    privilegio_usuario: str
    status_usuario: str
