from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import Depends
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.orm import Session

from app.db import obter_sessao
from app.dependencies import UsuarioAtual, obter_agora, obter_fuso
from app.models import Recurso, Reserva
from app.repositories.recurso import RecursoRepository
from app.repositories.reserva import ReservaRepository
from app.schemas.reserva import ReservaCriar, ReservaResposta
from app.services.excecoes import (
    ConvidadosAcimaDaOcupacao,
    ForaDoHorario,
    RecursoInativo,
    RecursoNaoEncontrado,
    ReservaNaoCancelavel,
    ReservaNaoEncontrada,
    ReservaNoPassado,
)


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
    local_inicio = inicio.astimezone(fuso)
    local_fim = fim.astimezone(fuso)
    mesmo_dia = local_inicio.date() == local_fim.date()
    abre_antes = recurso.hora_func_inicio <= local_inicio.time()
    fecha_depois = recurso.hora_func_fim >= local_fim.time()
    return mesmo_dia and abre_antes and fecha_depois


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
        recurso = self._recursos.buscar_por_id(dados.id_recurso)
        if recurso is None:
            raise RecursoNaoEncontrado
        if recurso.status_recurso != "ativo":
            raise RecursoInativo
        if dados.inicio < self._agora:
            raise ReservaNoPassado
        if not cabe_no_horario(dados.inicio, dados.fim, recurso, self._fuso):
            raise ForaDoHorario
        if dados.convidados > recurso.ocupacao:
            raise ConvidadosAcimaDaOcupacao

        reserva = Reserva(
            id_usuario=usuario.id_usuario,
            id_recurso=dados.id_recurso,
            convidados=dados.convidados,
            periodo=Range(dados.inicio, dados.fim, bounds="[)"),
            status_reserva="confirmada",
        )
        reserva = self._reservas.criar(reserva)
        return self._para_resposta(reserva)

    def listar(
        self, usuario: UsuarioAtual, limite: int, deslocamento: int
    ) -> list[ReservaResposta]:
        eh_admin = usuario.privilegio_usuario == "admin"
        id_usuario = None if eh_admin else usuario.id_usuario
        reservas = self._reservas.listar(limite, deslocamento, id_usuario)
        return [self._para_resposta(reserva) for reserva in reservas]

    def buscar_por_id(self, id_reserva: int, usuario: UsuarioAtual) -> ReservaResposta:
        reserva = self._reservas.buscar_por_id(id_reserva)
        reserva = garantir_acesso(reserva, usuario)
        # levanta: ReservaNaoEncontrada
        return self._para_resposta(reserva)

    def cancelar(self, id_reserva: int, usuario: UsuarioAtual) -> ReservaResposta:
        # levanta: ReservaNaoEncontrada, ReservaNaoCancelavel
        reserva = self._reservas.buscar_por_id(id_reserva)
        reserva = garantir_acesso(reserva, usuario)
        cancelou = self._reservas.cancelar(id_reserva, usuario.id_usuario, self._agora)
        if not cancelou:
            raise ReservaNaoCancelavel
        return self._para_resposta(reserva)

    def _para_resposta(self, reserva: Reserva) -> ReservaResposta:
        inicio = reserva.periodo.lower
        fim = reserva.periodo.upper
        # O CHECK formato_semiaberto proíbe período sem uma das pontas.
        # O assert conta isso ao mypy.
        assert inicio is not None and fim is not None
        return ReservaResposta(
            id_reserva=reserva.id_reserva,
            id_usuario=reserva.id_usuario,
            id_recurso=reserva.id_recurso,
            convidados=reserva.convidados,
            inicio=inicio,
            fim=fim,
            status_reserva=status_efetivo(reserva, self._agora),
            cancelada_por_id_usuario=reserva.cancelada_por_id_usuario,
            cancelada_em=reserva.cancelada_em,
        )
