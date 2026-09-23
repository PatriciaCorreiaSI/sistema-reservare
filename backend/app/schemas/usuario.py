from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCriar(BaseModel):
    nome_usuario: str = Field(min_length=1)
    email_usuario: EmailStr
    senha: str = Field(min_length=8)
    privilegio_usuario: Literal["admin", "usuario"]


class UsuarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    nome_usuario: str
    email_usuario: str
    privilegio_usuario: str
    status_usuario: str
