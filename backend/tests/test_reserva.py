from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.dialects.postgresql import Range

from app.dependencies import obter_agora, obter_fuso
from app.main import app
from app.models import Reserva

pendente = pytest.mark.skip(reason="Etapa 4, fase Tentar: corpo ainda não escrito")

AGORA = datetime(2026, 10, 1, 12, 0, tzinfo=UTC)
FUSO = ZoneInfo("America/Sao_Paulo")


@pytest.fixture(autouse=True)
def agora_fixo():
    # Troca obter_agora por AGORA (dependency_overrides) em todo teste do arquivo,
    # e desfaz a troca no fim.
    app.dependency_overrides[obter_agora] = lambda: AGORA
    yield
    app.dependency_overrides.pop(obter_agora, None)


@pytest.fixture(autouse=True)
def fuso_fixo():
    # Troca obter_fuso por ZoneInfo("America/Sao_Paulo") em todo teste do arquivo,
    # e desfaz a troca no fim.
    app.dependency_overrides[obter_fuso] = lambda: FUSO
    yield
    app.dependency_overrides.pop(obter_fuso, None)


@pytest.fixture
def reserva_da_ana(sessao, usuario, recurso_criado):
    # Grava pelo modelo, sem HTTP: confirmada, no dia seguinte a AGORA, das 10h às 11h
    # no horário de Brasília (13h às 14h UTC). Devolve o objeto Reserva.
    # Prepara recurso, usuário e reserva
    periodo = Range(
        datetime(2026, 10, 2, 13, 0, tzinfo=UTC),
        datetime(2026, 10, 2, 14, 0, tzinfo=UTC),
        bounds="[)",
    )

    reserva = Reserva(
        id_usuario=usuario.id_usuario,
        id_recurso=recurso_criado["id_recurso"],
        convidados=7,
        periodo=periodo,
        status_reserva="confirmada",
    )
    sessao.add(reserva)
    sessao.flush()
    return reserva


# POST /reservas


@pendente
def test_criar_reserva_devolve_201_confirmada_em_nome_de_quem_chama(
    client, usuario, recurso_criado, cabecalho_de
):
    """201, status_reserva 'confirmada'; id_usuario é o Ana, vindo do token."""


@pendente
def test_criar_reserva_sem_token_devolve_401(client, recurso_criado):
    """Corpo válido, sem o cabeçalho Authorization → 401."""


@pendente
def test_criar_reserva_sem_fuso_devolve_422(
    client, usuario, recurso_criado, cabecalho_de
):
    """inicio sem deslocamento ('2026-10-02T10:00') → 422, recusado no schema."""


@pendente
def test_criar_reserva_com_inicio_igual_ao_fim_devolve_422(
    client, usuario, recurso_criado, cabecalho_de
):
    """inicio == fim → 422, recusado no model_validator do schema."""


@pendente
def test_criar_reserva_no_passado_devolve_422(
    client, usuario, recurso_criado, cabecalho_de
):
    """inicio antes de AGORA → 422 (ReservaNoPassado)."""


@pendente
def test_criar_reserva_fora_do_horario_devolve_422(
    client, usuario, recurso_criado, cabecalho_de
):
    """Recurso das 8h às 18h, reseva das 18h às 19h locais → 422 (ForaDohorario)."""


@pendente
def test_criar_reserva_acima_da_ocupacao_devolve_422(
    client, usuario, recurso_criado, cabecalho_de
):
    """Ocupação 10, convidados 11 → 422 (ConvidadosAcimaDaOcupacao)."""


@pendente
def test_criar_reserva_em_recurso_inexistente_devolve_404(
    client, usuario, cabecalho_de
):
    """id_recurso 999999 → 404."""


@pendente
def test_criar_reserva_em_recurso_inativo_devolve_409(
    client, usuario, recurso_criado, cabecalho_de
):
    """Recurso inativo antes, pelo PATCH → 409 (RecursoInativo)."""


@pendente
def test_criar_reserva_sobreposta_devolve_409(
    client, usuario, reserva_da_ana, cabecalho_de
):
    """Mesmo recurso, 10h30 às 11h30 sobre a reserva das 10h às 11h → 409
    (HorarioOcupado). Critério de pronto: é a EXCLUDE recusando, traduzida
    pelo ADR 0014.
    """


@pendente
def test_criar_reserva_encostada_devolve_201(
    client, usuario, reserva_da_ana, cabecalho_de
):
    """Das 11h às 12h, logo depois da reserva das 10h às 11h → 201:
    encostar não é sobrepor."""


# GET /reservas


@pendente
def test_listar_reservas_devolve_so_as_da_usuaria(
    client, outra_usuaria, reserva_da_ana, cabecalho_de
):
    """A outra usuária lista e não recebe a reserva da Ana."""


@pendente
def test_listar_reservas_devolve_todas_ao_admin(
    client, admin, reserva_da_ana, cabecalho_de
):
    """O admin lista e recebe a reseva da Ana."""


# GET /reservas/{id}


def test_buscar_reserva_da_dona_devolve_200(
    client, usuario, reserva_da_ana, cabecalho_de
):
    # A Ana busca a própria reserva → 200, com inicio e fim separados do periodo.
    # Preparar: as fixtures já gravaram a Ana, o recurso e a reserva.

    # Agir
    resposta = client.get(
        f"/reservas/{reserva_da_ana.id_reserva}", headers=cabecalho_de(usuario)
    )

    # Conferir
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["id_reserva"] == reserva_da_ana.id_reserva
    assert datetime.fromisoformat(corpo["inicio"]) == reserva_da_ana.periodo.lower
    assert datetime.fromisoformat(corpo["fim"]) == reserva_da_ana.periodo.upper


def test_buscar_reserva_alheia_devolve_404(
    client, outra_usuaria, reserva_da_ana, cabecalho_de
):
    # IDOR, critério de pronto: a outra usuária busca a reserva da Ana → 404.
    # Preparar: as fixtures já gravaram a Ana, a outra usuária, o recurso e a reserva

    # Agir
    resposta = client.get(
        f"/reservas/{reserva_da_ana.id_reserva}", headers=cabecalho_de(outra_usuaria)
    )

    # Conferir
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Reserva não encontrada"


def test_buscar_reserva_inexistente_devolve_404(client, usuario, cabecalho_de):
    # id 9999999 → 404, a mesma resposta do teste anterior.
    # Preparar: uso de id inexistente

    # Agir
    resposta = client.get("/reservas/9999999", headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 404


@pendente
def test_buscar_reserva_alheia_como_admin_devolve_200(
    client, admin, reserva_da_ana, cabecalho_de
):
    """O admin busca a reserva da Ana → 200."""


@pendente
def test_buscar_reserva_terminada_devolve_status_concluida(
    client, usuario, reserva_da_ana, cabecalho_de
):
    """Troca o relógio de novo, para depois do fim → status_reserva 'concluida',
    embora a coluna diga 'confirmada' (status efetivo, ADR 0004)."""


# POST /reservas/{id}/cancelar


@pendente
def test_cancelar_reserva_da_dona_devolve_200_cancelada(
    client, usuario, reserva_da_ana, cabecalho_de
):
    """200; status_reserva 'cancelada'; 'cancelada_por_id_usuario' é a Ana;
    'cancelada_em' é AGORA. Pega a armadilha do identity map."""


@pendente
def test_cancelar_reserva_alheia_como_admin_devolve_200(
    client, admin, reserva_da_ana, cabecalho_de
):
    """O admin cancela a reserva da Ana → 200; 'cancelada_por_id_usuario' é o admin."""


@pendente
def test_cancelar_reserva_alheia_devolve_404(
    client, outra_usuaria, reserva_da_ana, cabecalho_de
):
    """IDOR, critério de pronto: a outra usuária cancela a reserva da Ana → 404."""


@pendente
def test_cancelar_reserva_ja_cancelada_devolve_409(
    client, usuario, reserva_da_ana, cabecalho_de
):
    """Cancelar duas vezes → a segunda devolve 409 (ReservaNaoCancelavel)."""


@pendente
def test_cancelar_reserva_terminada_devolve_409(
    client, usuario, reserva_da_ana, cabecalho_de
):
    """Troca o relógio de novo, para depois do fim → 409: 'concluída' é final
    (ADR 0016)."""


@pendente
def test_cancelar_reserva_libera_o_horario(
    client, usuario, reserva_da_ana, cabecalho_de
):
    """Depois de cancelar, cria uma reserva nova no mesmo período → 201: a EXCLUDE só
    olha reservas com 'cancelada_em' nulo."""
