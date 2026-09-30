from collections.abc import Sequence
from datetime import datetime

import psycopg
from sqlalchemy import CursorResult, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Reserva
from app.services.excecoes import HorarioOcupado, RecursoNaoEncontrado

SEM_SOBREPOSICAO = "ex_reserva_sem_sobreposicao"
FK_RECURSO = "fk_reserva_id_recurso_recurso"


class ReservaRepository:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def buscar_por_id(self, id_reserva: int) -> Reserva | None:
        consulta = select(Reserva).where(Reserva.id_reserva == id_reserva)
        return self._sessao.scalar(consulta)

    def listar(
        self, limite: int, deslocamento: int, id_usuario: int | None
    ) -> Sequence[Reserva]:
        consulta = select(Reserva)
        if id_usuario is not None:
            consulta = consulta.where(Reserva.id_usuario == id_usuario)
        consulta = (
            consulta.order_by(Reserva.id_reserva).limit(limite).offset(deslocamento)
        )
        return self._sessao.scalars(consulta).all()

    def criar(self, reserva: Reserva) -> Reserva:
        # levanta: HorarioOcupado, RecursoNaoEncontrado (ADR 0014)
        self._sessao.add(reserva)
        try:
            self._sessao.flush()
        except IntegrityError as erro:
            if not isinstance(erro.orig, psycopg.Error):
                raise
            constraint = erro.orig.diag.constraint_name
            if constraint == SEM_SOBREPOSICAO:
                raise HorarioOcupado from erro
            if constraint == FK_RECURSO:
                raise RecursoNaoEncontrado from erro
            raise
        return reserva

    def cancelar(self, id_reserva: int, cancelada_por_id: int, agora: datetime) -> bool:
        comando = (
            update(Reserva)
            .where(
                Reserva.id_reserva == id_reserva,
                Reserva.cancelada_em.is_(None),
                func.upper(Reserva.periodo) > agora,
            )
            .values(
                status_reserva="cancelada",
                cancelada_em=agora,
                cancelada_por_id_usuario=cancelada_por_id,
            )
        )
        resultado = self._sessao.execute(comando)
        assert isinstance(resultado, CursorResult)
        return resultado.rowcount == 1

    def listar_ativas_na_janela(
        self,
        id_recurso: int,
        janela_inicio: datetime,
        janela_fim: datetime,
    ) -> Sequence[Reserva]:
        # devolve ordenado por início do período
        raise NotImplementedError
