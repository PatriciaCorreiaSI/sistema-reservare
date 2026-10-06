from pydantic import BaseModel


class LoginEntrada(BaseModel):
    email_usuario: str
    senha: str


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"
