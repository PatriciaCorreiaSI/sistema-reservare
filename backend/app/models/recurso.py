from datetime import time

from sqlalchemy import CheckConstraint, Identity, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Recurso(Base):
    __tablename__ = "recurso"

    id_recurso: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    nome_recurso: Mapped[str] = mapped_column(String(30))
    ocupacao: Mapped[int] = mapped_column()
    hora_func_inicio: Mapped[time] = mapped_column(Time())
    hora_func_fim: Mapped[time] = mapped_column(Time())
    status_recurso: Mapped[str] = mapped_column(String(30))

    __table_args__ = (
        CheckConstraint("status_recurso IN ('ativo', 'inativo')", name="status"),
        CheckConstraint("ocupacao > 0", name="ocupacao_positiva"),
        CheckConstraint(
            "hora_func_inicio < hora_func_fim", name="horario_dentro_do_dia"
        ),
    )
