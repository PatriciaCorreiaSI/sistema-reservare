from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.dialects.postgresql import Range

from app.dependencies import obter_agora, obter_fuso
from app.main import app
from app.models import Reserva

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
    sessao.commit()
    return reserva


# POST /reservas


def test_criar_reserva_devolve_201_confirmada_em_nome_de_quem_chama(
    client, usuario, recurso_criado, cabecalho_de
):
    # 201, status_reserva 'confirmada'; id_usuario é o Ana, vindo do token.
    # Preparar: o corpo do pedido, no formato do ReservaCriar. Sem id_usuario:
    # quem é a dona o app descobre pelo token
    reserva = {
        "id_recurso": recurso_criado["id_recurso"],
        "convidados": 4,
        "inicio": "2026-10-01T15:00:00Z",
        "fim": "2026-10-01T16:00:00Z",
    }

    # Agir
    resposta = client.post("/reservas", json=reserva, headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status_reserva"] == "confirmada"
    assert corpo["id_usuario"] == usuario.id_usuario


def test_criar_reserva_sem_token_devolve_401(client, recurso_criado):
    # Corpo válido, sem o cabeçalho Authorization → 401.
    # Preparar: o corpo do pedido, no formato do ReservaCriar.
    reserva = {
        "id_recurso": recurso_criado["id_recurso"],
        "convidados": 4,
        "inicio": "2026-10-01T15:00:00Z",
        "fim": "2026-10-01T16:00:00Z",
    }

    # Agir: sem token
    resposta = client.post("/reservas", json=reserva)

    # Conferir
    assert resposta.status_code == 401


def test_criar_reserva_sem_fuso_devolve_422(
    client, usuario, recurso_criado, cabecalho_de
):
    # inicio sem deslocamento ('2026-10-02T10:00') → 422, recusado no schema.
    # Preparar: o corpo do pedido, no formato do ReservaCriar.
    reserva = {
        "id_recurso": recurso_criado["id_recurso"],
        "convidados": 4,
        "inicio": "2026-10-01T15:00:00",
        "fim": "2026-10-01T16:00:00Z",
    }

    # Agir
    resposta = client.post("/reservas", json=reserva, headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 422


def test_criar_reserva_com_inicio_igual_ao_fim_devolve_422(
    client, usuario, recurso_criado, cabecalho_de
):
    # inicio == fim → 422, recusado no model_validator do schema.
    # Preparar: o corpo do pedido, no formato do ReservaCriar. Sem id_usuario:
    reserva = {
        "id_recurso": recurso_criado["id_recurso"],
        "convidados": 4,
        "inicio": "2026-10-01T15:00:00Z",
        "fim": "2026-10-01T15:00:00Z",
    }

    # Agir
    resposta = client.post("/reservas", json=reserva, headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 422


def test_criar_reserva_no_passado_devolve_422(
    client, usuario, recurso_criado, cabecalho_de
):
    # inicio antes de AGORA → 422 (ReservaNoPassado).
    # AGORA = datetime(2026, 10, 1, 12, 0, tzinfo=UTC)
    # Preparar: o corpo do pedido, no formato do ReservaCriar.
    reserva = {
        "id_recurso": recurso_criado["id_recurso"],
        "convidados": 4,
        "inicio": "2026-09-30T15:00:00Z",
        "fim": "2026-09-30T16:00:00Z",
    }

    # Agir
    resposta = client.post("/reservas", json=reserva, headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 422


def test_criar_reserva_fora_do_horario_devolve_422(
    client, usuario, recurso_criado, cabecalho_de
):
    # Recurso das 8h às 18h, reseva das 18h às 19h locais → 422 (ForaDohorario).
    reserva = {
        "id_recurso": recurso_criado["id_recurso"],
        "convidados": 4,
        "inicio": "2026-10-01T21:00:00Z",
        "fim": "2026-10-01T22:00:00Z",
    }

    # Agir
    resposta = client.post("/reservas", json=reserva, headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 422


def test_criar_reserva_acima_da_ocupacao_devolve_422(
    client, usuario, recurso_criado, cabecalho_de
):
    # Ocupação 10, convidados 11 → 422 (ConvidadosAcimaDaOcupacao).
    reserva = {
        "id_recurso": recurso_criado["id_recurso"],
        "convidados": 11,
        "inicio": "2026-10-01T15:00:00Z",
        "fim": "2026-10-01T16:00:00Z",
    }

    # Agir
    resposta = client.post("/reservas", json=reserva, headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 422


def test_criar_reserva_em_recurso_inexistente_devolve_404(
    client, usuario, cabecalho_de
):
    # id_recurso 999999 → 404.
    # Preparar: o corpo do pedido, no formato do ReservaCriar. Sem id_usuario:
    reserva = {
        "id_recurso": 999999,
        "convidados": 4,
        "inicio": "2026-10-01T15:00:00Z",
        "fim": "2026-10-01T16:00:00Z",
    }

    # Agir
    resposta = client.post("/reservas", json=reserva, headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 404


def test_criar_reserva_em_recurso_inativo_devolve_409(
    client, usuario, recurso_criado, cabecalho_de, admin
):
    # Recurso inativo antes, pelo PATCH → 409 (RecursoInativo).
    # Preparar: o corpo do pedido, no formato do ReservaCriar. Sem id_usuario:
    resposta = client.patch(
        f"/recursos/{recurso_criado['id_recurso']}",
        json={"status_recurso": "inativo"},
        headers=cabecalho_de(admin),
    )
    assert resposta.status_code == 200
    reserva = {
        "id_recurso": recurso_criado["id_recurso"],
        "convidados": 4,
        "inicio": "2026-10-01T15:00:00Z",
        "fim": "2026-10-01T16:00:00Z",
    }

    # Agir
    resposta = client.post("/reservas", json=reserva, headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 409


def test_criar_reserva_sobreposta_devolve_409(
    client, usuario, reserva_da_ana, cabecalho_de
):
    # Mesmo recurso, 10h30 às 11h30 sobre a reserva das 10h às 11h → 409
    # (HorarioOcupado). Critério de pronto: é a EXCLUDE recusando, traduzida
    # pelo ADR 0014.
    reserva = {
        "id_recurso": reserva_da_ana.id_recurso,
        "convidados": 4,
        "inicio": "2026-10-02T13:30:00Z",
        "fim": "2026-10-02T14:30:00Z",
    }

    # Agir
    resposta = client.post("/reservas", json=reserva, headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 409


def test_criar_reserva_encostada_devolve_201(
    client, usuario, reserva_da_ana, cabecalho_de
):
    # Das 11h às 12h, logo depois da reserva das 10h às 11h → 201:
    # encostar não é sobrepor.
    reserva = {
        "id_recurso": reserva_da_ana.id_recurso,
        "convidados": 4,
        "inicio": "2026-10-02T14:00:00Z",
        "fim": "2026-10-02T15:00:00Z",
    }

    # Agir
    resposta = client.post("/reservas", json=reserva, headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 201


# GET /reservas


def test_listar_reservas_devolve_so_as_da_usuaria(
    client, outra_usuaria, reserva_da_ana, cabecalho_de
):
    # A outra usuária lista e não recebe a reserva da Ana.
    # Preparar: as fixtures já gravaram a Ana, o recurso e a reserva.

    # Agir
    resposta = client.get("/reservas", headers=cabecalho_de(outra_usuaria))

    # Conferir
    assert resposta.status_code == 200
    ids = [r["id_reserva"] for r in resposta.json()]
    assert reserva_da_ana.id_reserva not in ids


def test_listar_reservas_devolve_todas_ao_admin(
    client, admin, reserva_da_ana, cabecalho_de
):
    # O admin lista e recebe a reseva da Ana.
    # Preparar: as fixtures já gravaram a Ana, o recurso e a reserva.

    # Agir
    resposta = client.get("/reservas", headers=cabecalho_de(admin))

    # Conferir
    assert resposta.status_code == 200
    ids = [r["id_reserva"] for r in resposta.json()]
    assert reserva_da_ana.id_reserva in ids


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


def test_buscar_reserva_alheia_como_admin_devolve_200(
    client, admin, reserva_da_ana, cabecalho_de
):
    # O admin busca a reserva da Ana → 200.
    # Preparar: as fixtures já gravaram a Ana, o admin, o recurso e a reserva

    # Agir
    resposta = client.get(
        f"/reservas/{reserva_da_ana.id_reserva}", headers=cabecalho_de(admin)
    )

    # Conferir
    assert resposta.status_code == 200


def test_buscar_reserva_terminada_devolve_status_concluida(
    client, usuario, reserva_da_ana, cabecalho_de
):
    # Troca o relógio de novo, para depois do fim → status_reserva 'concluida',
    # embora a coluna diga 'confirmada' (status efetivo, ADR 0004).
    # Preparar: o fim da reserva já está na fixture: reserva_da_ana.periodo.upper.
    # Lendo dela, a data não pode divergir.
    # A limpeza é da agora_fixo, que faz o popo no fim de todo teste.
    app.dependency_overrides[obter_agora] = lambda: reserva_da_ana.periodo.upper

    # Agir
    resposta = client.get(
        f"/reservas/{reserva_da_ana.id_reserva}", headers=cabecalho_de(usuario)
    )

    # Conferir
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status_reserva"] == "concluida"


# POST /reservas/{id}/cancelar


def test_cancelar_reserva_da_dona_devolve_200_cancelada(
    client, usuario, reserva_da_ana, cabecalho_de
):
    # 200; status_reserva 'cancelada'; 'cancelada_por_id_usuario' é a Ana;
    # 'cancelada_em' é AGORA. Pega a armadilha do identity map.
    # Preparar: as fixtures já gravaram a Ana, o recurso e a reserva
    # Agir
    resposta = client.post(
        f"/reservas/{reserva_da_ana.id_reserva}/cancelar", headers=cabecalho_de(usuario)
    )

    # Conferir
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status_reserva"] == "cancelada"
    assert corpo["cancelada_por_id_usuario"] == usuario.id_usuario
    assert datetime.fromisoformat(corpo["cancelada_em"]) == AGORA


def test_cancelar_reserva_alheia_como_admin_devolve_200(
    client, admin, reserva_da_ana, cabecalho_de
):
    # O admin cancela a reserva da Ana → 200; 'cancelada_por_id_usuario' é o admin.
    # Preparar: as fixtures já gravaram a Ana, o recurso e a reserva
    # Agir
    resposta = client.post(
        f"/reservas/{reserva_da_ana.id_reserva}/cancelar", headers=cabecalho_de(admin)
    )

    # Conferir
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status_reserva"] == "cancelada"
    assert corpo["cancelada_por_id_usuario"] == admin.id_usuario
    assert datetime.fromisoformat(corpo["cancelada_em"]) == AGORA


def test_cancelar_reserva_alheia_devolve_404(
    client, usuario, outra_usuaria, reserva_da_ana, cabecalho_de
):
    # IDOR, critério de pronto: a outra usuária cancela a reserva da Ana → 404.
    # Preparar: as fixtures já gravaram a Ana, o recurso, a reserva e a outra usuária
    # Agir
    resposta = client.post(
        f"/reservas/{reserva_da_ana.id_reserva}/cancelar",
        headers=cabecalho_de(outra_usuaria),
    )

    # Conferir: a resposta é a mesma da reserva inexistente (ADR 0017)...
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Reserva não encontrada"

    # ...e a reserva da Ana continua confirmada
    leitura = client.get(
        f"/reservas/{reserva_da_ana.id_reserva}", headers=cabecalho_de(usuario)
    )
    assert leitura.status_code == 200
    assert leitura.json()["status_reserva"] == "confirmada"


def test_cancelar_reserva_ja_cancelada_devolve_409(
    client, usuario, reserva_da_ana, cabecalho_de
):
    # Cancelar duas vezes → a segunda devolve 409 (ReservaNaoCancelavel).
    # Preparar: o primeiro cancelamento pela API
    url = f"/reservas/{reserva_da_ana.id_reserva}/cancelar"
    primeira = client.post(url, headers=cabecalho_de(usuario))
    assert primeira.status_code == 200

    # Agir: o segundo cancelamento
    resposta = client.post(url, headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "A reserva já foi cancelada ou já terminou"


def test_cancelar_reserva_terminada_devolve_409(
    client, usuario, reserva_da_ana, cabecalho_de
):
    # Troca o relógio de novo, para depois do fim → 409: 'concluída' é final
    # (ADR 0016).
    # Preparar: o relógio exatamente no fim da reserva (a fronteira)
    app.dependency_overrides[obter_agora] = lambda: reserva_da_ana.periodo.upper

    # Agir
    resposta = client.post(
        f"/reservas/{reserva_da_ana.id_reserva}/cancelar", headers=cabecalho_de(usuario)
    )

    # Conferir: recusado, e a reserva segue concluída, não cancelada
    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "A reserva já foi cancelada ou já terminou"
    leitura = client.get(
        f"/reservas/{reserva_da_ana.id_reserva}", headers=cabecalho_de(usuario)
    )
    assert leitura.status_code == 200
    assert leitura.json()["status_reserva"] == "concluida"


def test_cancelar_reserva_libera_o_horario(
    client, usuario, reserva_da_ana, cabecalho_de
):
    # Depois de cancelar, cria uma reserva nova no mesmo período → 201: a EXCLUDE só
    # olha reservas com 'cancelada_em' nulo.
    # Preparar: a Ana cancela a reserva das 10h às 11h (13h às 14h UTC)
    cancelamento = client.post(
        f"/reservas/{reserva_da_ana.id_reserva}/cancelar", headers=cabecalho_de(usuario)
    )
    assert cancelamento.status_code == 200

    # Agir: uma reserva nova exatamente no mesmo período
    reserva = {
        "id_recurso": reserva_da_ana.id_recurso,
        "convidados": 4,
        "inicio": "2026-10-02T13:00:00Z",
        "fim": "2026-10-02T14:00:00Z",
    }
    resposta = client.post("/reservas", json=reserva, headers=cabecalho_de(usuario))

    # Conferir
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["status_reserva"] == "confirmada"


# GET /recursos/{id}/disponibilidade


def test_disponibilidade_sem_token_devolve_401(client, recurso_criado):
    # Sem Authorization → 401 com WWW-Authenticate: Bearer.
    # Preparar: o recurso vem da fixture; o id vai na URL
    id_recurso = recurso_criado["id_recurso"]
    # Agir: sem token
    resposta = client.get(
        f"/recursos/{id_recurso}/disponibilidade", params={"dia": "2026-10-02"}
    )
    # Conferir
    assert resposta.status_code == 401
    assert resposta.headers["WWW-Authenticate"] == "Bearer"


def test_disponibilidade_com_dia_mal_formado_devolve_422(
    client, recurso_criado, usuario, cabecalho_de
):
    # ?dia=2026-13-40 → 422 (o tipo date recusa antes do service).
    # Preparar: o recurso vem da fixture; o id vai na URL
    id_recurso = recurso_criado["id_recurso"]
    # Agir: com token
    resposta = client.get(
        f"/recursos/{id_recurso}/disponibilidade",
        params={"dia": "2026-13-40"},
        headers=cabecalho_de(usuario),
    )
    # Conferir
    assert resposta.status_code == 422


def test_disponibilidade_de_recurso_inexistente_devolve_404(
    client, recurso_criado, usuario, cabecalho_de
):
    # id que não existe → 404.
    # Preparar: o recurso vem da fixture; o id vai na URL;
    # a sequencia do Postgres só avança
    # então o próximo id (id_recurso + 1) nunca foi usado
    id_recurso = recurso_criado["id_recurso"] + 1
    # Agir: com token
    resposta = client.get(
        f"/recursos/{id_recurso}/disponibilidade",
        params={"dia": "2026-10-02"},
        headers=cabecalho_de(usuario),
    )
    # Conferir
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Recurso não encontrado"


def test_disponibilidade_de_recurso_inativo_devolve_409(
    client, recurso_criado, usuario, cabecalho_de, admin
):
    # PATCH para inativo (com assert do status) antes → 409.
    # Preparar
    resposta = client.patch(
        f"/recursos/{recurso_criado['id_recurso']}",
        json={"status_recurso": "inativo"},
        headers=cabecalho_de(admin),
    )
    assert resposta.status_code == 200
    # Agir: o mesmo GET, id real, dia válido e token
    id_recurso = recurso_criado["id_recurso"]
    resposta = client.get(
        f"/recursos/{id_recurso}/disponibilidade",
        params={"dia": "2026-10-02"},
        headers=cabecalho_de(usuario),
    )
    # Conferir
    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Recurso inativo não aceita reservas"


def test_disponibilidade_de_dia_livre_devolve_a_janela_inteira_em_utc(
    client, recurso_criado, usuario, cabecalho_de
):
    # dia=2026-10-03, sem reservas → uma lacuna: 11h-21h UTC (8h-18h local);
    # dia ecoado na resposta.
    # Preparar
    id_recurso = recurso_criado["id_recurso"]
    # Agir
    resposta = client.get(
        f"/recursos/{id_recurso}/disponibilidade",
        params={"dia": "2026-10-03"},
        headers=cabecalho_de(usuario),
    )
    corpo = resposta.json()
    # Conferir
    assert resposta.status_code == 200
    assert corpo["dia"] == "2026-10-03"
    assert len(corpo["lacunas"]) == 1
    assert datetime.fromisoformat(corpo["lacunas"][0]["inicio"]) == datetime(
        2026, 10, 3, 11, 0, tzinfo=UTC
    )
    assert datetime.fromisoformat(corpo["lacunas"][0]["fim"]) == datetime(
        2026, 10, 3, 21, 0, tzinfo=UTC
    )


def test_disponibilidade_com_reserva_devolve_as_lacunas_em_volta(
    client, recurso_criado, usuario, cabecalho_de, reserva_da_ana
):
    # dia=2026-10-02, com a reserva_da_ana (13h-14h UTC) → 11h-13h e 14h-21h.
    # Preparar: o recurso e a reserva vêm da fixture
    id_recurso = recurso_criado["id_recurso"]
    # Agir
    resposta = client.get(
        f"/recursos/{id_recurso}/disponibilidade",
        params={"dia": "2026-10-02"},
        headers=cabecalho_de(usuario),
    )
    # Conferir
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo["lacunas"]) == 2
    primeira, segunda = corpo["lacunas"]
    assert datetime.fromisoformat(primeira["inicio"]) == datetime(
        2026, 10, 2, 11, 0, tzinfo=UTC
    )
    assert datetime.fromisoformat(primeira["fim"]) == datetime(
        2026, 10, 2, 13, 0, tzinfo=UTC
    )
    assert datetime.fromisoformat(segunda["inicio"]) == datetime(
        2026, 10, 2, 14, 0, tzinfo=UTC
    )
    assert datetime.fromisoformat(segunda["fim"]) == datetime(
        2026, 10, 2, 21, 0, tzinfo=UTC
    )


def test_disponibilidade_nao_revela_quem_reservou(
    client, recurso_criado, usuario, cabecalho_de, reserva_da_ana
):
    # A resposta não tem id_usuario nem convidados em lugar nenhum (ADR 00017).
    # Preparar: o recurso e a reserva vêm da fixture
    id_recurso = recurso_criado["id_recurso"]
    # Agir
    resposta = client.get(
        f"/recursos/{id_recurso}/disponibilidade",
        params={"dia": "2026-10-02"},
        headers=cabecalho_de(usuario),
    )
    # Conferir
    assert resposta.status_code == 200
    assert "id_usuario" not in resposta.text
    assert "convidados" not in resposta.text


def test_disponibilidade_corta_o_passado_no_agora(
    client, recurso_criado, usuario, cabecalho_de
):
    # dia=2026-10-01 (AGORA = 12h UTC) → a lacuna começa em 12h, não às 11h.
    # Preparar
    id_recurso = recurso_criado["id_recurso"]
    # Agir
    resposta = client.get(
        f"/recursos/{id_recurso}/disponibilidade",
        params={"dia": "2026-10-01"},
        headers=cabecalho_de(usuario),
    )
    # Conferir
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo["lacunas"]) == 1
    assert datetime.fromisoformat(corpo["lacunas"][0]["inicio"]) == AGORA
    assert datetime.fromisoformat(corpo["lacunas"][0]["fim"]) == datetime(
        2026, 10, 1, 21, 0, tzinfo=UTC
    )


def test_disponibilidade_do_dia_inteiro_no_passado_devolve_200_com_lista_vazia(
    client, recurso_criado, usuario, cabecalho_de
):
    # dia=2026-09-30 → 200 e lacunas == [].
    # Preparar
    id_recurso = recurso_criado["id_recurso"]
    # Agir
    resposta = client.get(
        f"/recursos/{id_recurso}/disponibilidade",
        params={"dia": "2026-09-30"},
        headers=cabecalho_de(usuario),
    )
    corpo = resposta.json()
    # Conferir
    assert resposta.status_code == 200
    assert corpo["dia"] == "2026-09-30"
    assert corpo["lacunas"] == []
    assert corpo["dia"] == "2026-09-30"


def test_disponibilidade_ignora_reserva_cancelada(
    client, recurso_criado, usuario, cabecalho_de, reserva_da_ana
):
    # Cancelar a reserva_da_ana (com assert do status) e consultar 2/10
    # → janela inteira.
    # Preparar: cancela a reserva_da_ana
    resposta = client.post(
        f"/reservas/{reserva_da_ana.id_reserva}/cancelar", headers=cabecalho_de(usuario)
    )
    assert resposta.status_code == 200
    # Agir
    id_recurso = recurso_criado["id_recurso"]
    resposta = client.get(
        f"/recursos/{id_recurso}/disponibilidade",
        params={"dia": "2026-10-02"},
        headers=cabecalho_de(usuario),
    )
    # Conferir
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo["lacunas"]) == 1
    assert datetime.fromisoformat(corpo["lacunas"][0]["inicio"]) == datetime(
        2026, 10, 2, 11, 0, tzinfo=UTC
    )
    assert datetime.fromisoformat(corpo["lacunas"][0]["fim"]) == datetime(
        2026, 10, 2, 21, 0, tzinfo=UTC
    )
