from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Usuario


class UsuarioRepository:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def buscar_por_email(self, email_usuario: str) -> Usuario | None:
        consulta = select(Usuario).where(Usuario.email_usuario == email_usuario)
        return self._sessao.scalar(consulta)

    def criar(self, usuario: Usuario) -> Usuario:
        self._sessao.add(usuario)
        self._sessao.flush()
        return usuario
