from sqlalchemy import CheckConstraint, Identity, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    privilegio_usuario: Mapped[str] = mapped_column(String(15))
    nome_usuario: Mapped[str] = mapped_column(String(30))
    email_usuario: Mapped[str] = mapped_column(String(50), unique=True)
    senha_usuario_hash: Mapped[str] = mapped_column(
        String(100), comment="Hash da senha do usuário, gerada por Argon 2"
    )
    status_usuario: Mapped[str] = mapped_column(String(30))

    __table_args__ = (
        CheckConstraint("status_usuario IN ('ativo', 'inativo')", name="status"),
        CheckConstraint(
            "privilegio_usuario IN ('admin', 'usuario')", name="privilegio"
        ),
    )
