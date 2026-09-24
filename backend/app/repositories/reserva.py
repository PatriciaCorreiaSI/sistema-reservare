from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Reserva


class ReservaRepository:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def buscar_por_id(self, id_reserva: int) -> Reserva | None:
        consulta = select(Reserva).where(Reserva.id_reserva == id_reserva)
        return self._sessao.scalar(consulta)

    def listar(
        self, limite: int, deslocamento: int, id_usuario: int | None
    ) -> Sequence[Reserva]:
        raise NotImplementedError

    def criar(self, reserva: Reserva) -> Reserva:
        # levanta: HorarioOcupado, RecursoNaoEncontrado (ADR 0014)
        raise NotImplementedError

    def cancelar(self, id_reserva: int, cancelada_por_id: int, agora: datetime) -> bool:
        raise NotImplementedError
