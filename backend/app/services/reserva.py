from datetime import datetime

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import obter_sessao
from app.dependencies import UsuarioAtual, obter_agora
from app.models import Reserva
from app.repositories.recurso import RecursoRepository
from app.repositories.reserva import ReservaRepository
from app.schemas.reserva import ReservaCriar, ReservaResposta


def status_efetivo(reserva: Reserva, agora: datetime) -> str:
    raise NotImplementedError


def garantir_acesso(reserva: Reserva | None, usuario: UsuarioAtual) -> Reserva:
    # levanta: ReservaNaoEncontrada (ADR 0017)
    raise NotImplementedError


class ReservaService:
    def __init__(
        self,
        sessao: Session = Depends(obter_sessao),
        agora: datetime = Depends(obter_agora),
    ) -> None:
        self._agora = agora
        self._reservas = ReservaRepository(sessao)
        self._recursos = RecursoRepository(sessao)

    def criar(self, dados: ReservaCriar, usuario: UsuarioAtual) -> ReservaResposta:
        # levanta: RecursoNaoEncontrado, RecursoInativo, ReservaNoPassado,
        # ForaDoHorario, ConvidadosAcimaDaOcupacao, HorarioOcupado
        raise NotImplementedError

    def listar(
        self, usuario: UsuarioAtual, limite: int, deslocamento: int
    ) -> list[ReservaResposta]:
        raise NotImplementedError

    def buscar_por_id(self, id_reserva: int, usuario: UsuarioAtual) -> ReservaResposta:
        # levanta: ReservaNaoEncontrada
        raise NotImplementedError

    def cancelar(self, id_reserva: int, usuario: UsuarioAtual) -> ReservaResposta:
        # levanta: ReservaNaoEncontrada, ReservaNaoCancelavel
        raise NotImplementedError

    def _para_resposta(self, reserva: Reserva) -> ReservaResposta:
        raise NotImplementedError
