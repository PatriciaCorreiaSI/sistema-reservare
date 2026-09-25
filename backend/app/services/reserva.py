from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import obter_sessao
from app.dependencies import UsuarioAtual, obter_agora, obter_fuso
from app.models import Recurso, Reserva
from app.repositories.recurso import RecursoRepository
from app.repositories.reserva import ReservaRepository
from app.schemas.reserva import ReservaCriar, ReservaResposta
from app.services.excecoes import ReservaNaoEncontrada


def status_efetivo(reserva: Reserva, agora: datetime) -> str:
    if reserva.status_reserva == "cancelada":
        return "cancelada"
    fim = reserva.periodo.upper
    # O CHECK formato_semiaberto proíbe período sem fim; o assert conta isso ao mypy.
    assert fim is not None
    if fim <= agora:
        return "concluida"
    return "confirmada"


def garantir_acesso(reserva: Reserva | None, usuario: UsuarioAtual) -> Reserva:
    # levanta: ReservaNaoEncontrada (ADR 0017)
    eh_admin = usuario.privilegio_usuario == "admin"
    if reserva is None or not (eh_admin or reserva.id_usuario == usuario.id_usuario):
        raise ReservaNaoEncontrada
    return reserva


def cabe_no_horario(
    inicio: datetime, fim: datetime, recurso: Recurso, fuso: ZoneInfo
) -> bool:
    hora_inicio = inicio.astimezone(fuso).time()
    hora_fim = fim.astimezone(fuso).time()
    abre_antes = recurso.hora_func_inicio <= hora_inicio
    fecha_depois = recurso.hora_func_fim >= hora_fim
    return abre_antes and fecha_depois


class ReservaService:
    def __init__(
        self,
        sessao: Session = Depends(obter_sessao),
        agora: datetime = Depends(obter_agora),
        fuso: ZoneInfo = Depends(obter_fuso),
    ) -> None:
        self._agora = agora
        self._fuso = fuso
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
