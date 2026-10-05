from datetime import UTC, datetime

import pytest
from sqlalchemy.dialects.postgresql import Range

from app.models import Reserva
from app.repositories.reserva import ReservaRepository
from app.services.excecoes import RecursoNaoEncontrado


def test_criar_com_recurso_inexistente_levanta_recurso_nao_encontrado(sessao, usuario):
    # ReservaRepository(sessao).criar(Reserva(...)) com todos os campos válidos
    # menos id_recurso, que aponta para um recurso que não existe
    # -> pytest.raises(RecursoNaoEncontrado).
    periodo = Range(
        datetime(2026, 10, 2, 13, 0, tzinfo=UTC),
        datetime(2026, 10, 2, 14, 0, tzinfo=UTC),
        bounds="[)",
    )
    reserva = Reserva(
        id_usuario=usuario.id_usuario,
        id_recurso=999_999,
        convidados=7,
        periodo=periodo,
        status_reserva="confirmada",
    )
    # Agir e conferir: o flush dispara a FK, e o repository a traduz pelo nome
    with pytest.raises(RecursoNaoEncontrado):
        ReservaRepository(sessao).criar(reserva)
