from datetime import UTC, datetime

import pytest
from sqlalchemy.dialects.postgresql import Range

from app.dependencies import UsuarioAtual
from app.models import Reserva
from app.services.excecoes import ReservaNaoEncontrada
from app.services.reserva import garantir_acesso, status_efetivo

pendente = pytest.mark.skip(reason="Etapa 4, fase Tentar: corpo ainda não escrito")

AGORA = datetime(2026, 10, 1, 12, 0, tzinfo=UTC)


# status_efetivo (ADR 0004 e 0016)


def test_status_efetivo_de_confirmada_com_fim_no_futuro_e_confirmada():
    # fim > agora → 'confirmada'
    # Preparar: confirmada, de 13h às 14h; AGORA é 12h, então o fim está no futuro
    reserva = Reserva(
        periodo=Range(
            datetime(2026, 10, 1, 13, 0, tzinfo=UTC),
            datetime(2026, 10, 1, 14, 0, 0, tzinfo=UTC),
            bounds="[)",
        ),
        status_reserva="confirmada",
    )
    # Agir
    status = status_efetivo(reserva, AGORA)
    # Conferir
    assert status == "confirmada"


def test_status_efetivo_de_confirmada_com_fim_igual_a_agora_e_concluida():
    # fim == agora → 'concluida': o intervalo é [inicio, fim), o fim não é ocupado.
    # Preparar: confirmada, de 11h às 12h; AGORA é 12h, então o fim está igual a agora
    reserva = Reserva(
        periodo=Range(
            datetime(2026, 10, 1, 11, 0, tzinfo=UTC),
            datetime(2026, 10, 1, 12, 0, 0, tzinfo=UTC),
            bounds="[)",
        ),
        status_reserva="confirmada",
    )
    # Agir
    status = status_efetivo(reserva, AGORA)
    # Conferir
    assert status == "concluida"


def test_status_efetivo_de_cancelada_com_fim_no_passado_continua_cancelada():
    # Cancelada é final: não vira 'concluida' quando o fim passa.
    # Preparar: cancelada, de 10h às 11h; AGORA é 12h, então o fim está no passado.
    reserva = Reserva(
        periodo=Range(
            datetime(2026, 10, 1, 10, 0, tzinfo=UTC),
            datetime(2026, 10, 1, 11, 0, 0, tzinfo=UTC),
            bounds="[)",
        ),
        status_reserva="cancelada",
    )
    # Agir
    status = status_efetivo(reserva, AGORA)
    # Conferir
    assert status == "cancelada"


# garantir_acesso (ADR 0017)


def test_garantir_acesso_devolve_a_reserva_a_dona():
    # Dona (id_usuario igual ao do token) → devolve a própria reserva.
    # Preparar: a reserva é da usuaria 1, e quem pede é a usuária 1
    usuario = UsuarioAtual(
        id_usuario=1,
        privilegio_usuario="usuario",
    )
    reserva = Reserva(id_usuario=1)
    # Agir
    devolvida = garantir_acesso(reserva, usuario)
    # Conferir
    assert devolvida is reserva


def test_garantir_acesso_devolve_a_reserva_ao_admin():
    # Admin, de outra pessoa → devolve a reserva.
    # Preparar: a reserva é da usuária 2, e quem pede é o admin, com privilégio
    usuario = UsuarioAtual(
        id_usuario=1,
        privilegio_usuario="admin",
    )
    reserva = Reserva(id_usuario=2)
    # Agir
    devolvida = garantir_acesso(reserva, usuario)
    # Conferir
    assert devolvida is reserva


def test_garantir_acesso_recusa_outra_usuaria():
    # Usuária comum, reserva alheia → ReservaNaoEncontrada.
    # Preparar: a reserva é da usuária 2, e quem pede é a usuária 1, sem privilégio
    usuario = UsuarioAtual(
        id_usuario=1,
        privilegio_usuario="usuario",
    )
    reserva = Reserva(id_usuario=2)
    # Agir e conferir
    with pytest.raises(ReservaNaoEncontrada):
        garantir_acesso(reserva, usuario)


def test_garantir_acesso_recusa_reserva_inexistente():
    # None → ReservaNaoEncontrada, a mesma exceção do caso anterior.
    # Preparar: quem pede é uma usuária comum; a reserva não existe (None)
    usuario = UsuarioAtual(
        id_usuario=1,
        privilegio_usuario="usuario",
    )
    # Agir e conferir
    with pytest.raises(ReservaNaoEncontrada):
        garantir_acesso(None, usuario)


# cabe_no_horario (ADR 0018), recurso das 08:00 às 18:00, fuso America/Sao_Paulo


@pendente
def test_cabe_no_horario_le_o_horario_no_fuso_do_sistema():
    """16:00-03:00 às 17:00-03:00 → True. Em UTC seria 19h às 20h, fora do horário:
    só passa se a comparação for feita no fuso do sistema."""


@pendente
def test_cabe_no_horario_aceita_fim_exatamente_no_efchamento():
    """17:00 às 18:00 local cabe: o fim não é ocupado."""


@pendente
def test_cabe_no_horario_recusa_inicio_antes_da_abertura():
    """07:59 às 09:00 local → False."""


@pendente
def test_cabe_no_horario_recusa_fim_depois_do_fechamento():
    """17:00 às 18:01 → False."""


@pendente
def test_cabe_no_horario_recusa_reserva_que_atravessa_a_meia_noite():
    """Das 17:00 de um dia às 09:00 do dia seguinte → False,
    mesmo com as duas pontas dentro do horário."""
