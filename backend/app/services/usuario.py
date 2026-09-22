from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import obter_sessao
from app.models import Usuario
from app.repositories.usuario import UsuarioRepository
from app.schemas.usuario import UsuarioCriar
from app.security import hasher
from app.services.excecoes import EmailJaCadastrado


class UsuarioService:
    def __init__(self, sessao: Session = Depends(obter_sessao)) -> None:
        self._repo = UsuarioRepository(sessao)

    def criar(self, dados: UsuarioCriar) -> Usuario:
        usuario = Usuario(
            nome_usuario=dados.nome_usuario,
            email_usuario=dados.email_usuario,
            privilegio_usuario=dados.privilegio_usuario,
            senha_usuario_hash=hasher.hash(dados.senha),
            status_usuario="ativo",
        )
        try:
            return self._repo.criar(usuario)
        except IntegrityError as erro:
            raise EmailJaCadastrado from erro
