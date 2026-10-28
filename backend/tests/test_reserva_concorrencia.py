import threading
from datetime import UTC, datetime, time
from time import monotonic, sleep
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.orm import sessionmaker

from app.db import obter_sessao
from app.dependencies import obter_agora, obter_fuso
from app.main import app
from app.models import Recurso, Reserva, Usuario
from app.security import criar_access_token

AGORA = datetime(2026, 10, 1, 12, 0, tzinfo=UTC)
FUSO = ZoneInfo("America/Sao_Paulo")
PRAZO = 10  # segundos que cada thread pode esperar antes de o teste falhar


@pytest.fixture
def fabrica_de_teste(engine_de_teste):
    # Como a FabricaDeSessao de app/db.py, mas ligada ao reservare_test.
    return sessionmaker(bind=engine_de_teste)


@pytest.fixture
def banco_limpo(engine_de_teste):
    # Não entrega nada: existe pela desmontagem. Roda mesmo se o teste falhar.
    yield
    with engine_de_teste.begin() as conexao:
        conexao.execute(text("TRUNCATE reserva, refresh_token, recurso, usuario"))


@pytest.fixture
def id_usuaria(banco_limpo, fabrica_de_teste):
    # Comita de verdade. Devolve o id, não o objeto: depois que a sessão
    # fecha, o objeto não pode mais ser lido.
    with fabrica_de_teste() as sessao, sessao.begin():
        usuaria = Usuario(
            privilegio_usuario="usuario",
            nome_usuario="Ana",
            email_usuario="ana@teste.com",
            senha_usuario_hash="nenhum-login-neste-teste",
            status_usuario="ativo",
        )
        sessao.add(usuaria)
        sessao.flush()
        id_lido = usuaria.id_usuario
    return id_lido


@pytest.fixture
def id_recurso(banco_limpo, fabrica_de_teste):
    with fabrica_de_teste() as sessao, sessao.begin():
        recurso = Recurso(
            nome_recurso="Sala 1",
            ocupacao=10,
            hora_func_inicio=time(8, 0),
            hora_func_fim=time(18, 0),
            status_recurso="ativo",
        )
        sessao.add(recurso)
        sessao.flush()
        id_lido = recurso.id_recurso
    return id_lido


@pytest.fixture
def api_com_sessao_real(fabrica_de_teste):
    # Repete o ciclo do obter_sessao de app/db.py; só a fábrica muda.
    def obter_sessao_real():
        sessao = fabrica_de_teste()
        try:
            yield sessao
            sessao.commit()
        except Exception:
            sessao.rollback()
            raise
        finally:
            sessao.close()

    app.dependency_overrides[obter_sessao] = obter_sessao_real
    app.dependency_overrides[obter_agora] = lambda: AGORA
    app.dependency_overrides[obter_fuso] = lambda: FUSO
    yield
    app.dependency_overrides.clear()


def reservar(corpo, cabecalho, barreira, status):
    # O que cada thread executa. guarda o status numa lista, porque o
    # retorno e as exceções de uma thread não chegam ao teste
    cliente = TestClient(app, base_url="https://testserver/api")
    barreira.wait()
    resposta = cliente.post("/reservas", json=corpo, headers=cabecalho)
    status.append(resposta.status_code)


@pytest.mark.concorrencia
def test_reservas_simultaneas_no_mesmo_horario_devolvem_um_201_e_um_409(
    api_com_sessao_real, id_usuaria, id_recurso
):
    # Duas threads, cada uma com o seu TestClient, liberadas por um Barrier.
    # O conjunto dos status é {201, 409}, sem depender de qual thread vence.
    # Preparar
    token = criar_access_token(id_usuaria, "usuario", datetime.now(UTC))
    cabecalho = {"Authorization": f"Bearer {token}"}
    corpo = {
        "id_recurso": id_recurso,
        "convidados": 4,
        "inicio": "2026-10-01T15:00:00Z",
        "fim": "2026-10-01T16:00:00Z",
    }
    barreira = threading.Barrier(2, timeout=PRAZO)
    status: list[int] = []
    threads = [
        threading.Thread(
            target=reservar, args=(corpo, cabecalho, barreira, status), daemon=True
        )
        for _ in range(2)
    ]

    # Agir
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=PRAZO)

    # Conferir
    assert not any(thread.is_alive() for thread in threads), "uma thread pendurou"
    assert sorted(status) == [201, 409]


@pytest.mark.concorrencia
def test_a_reserva_ja_esta_gravada_quando_o_201_sai(
    api_com_sessao_real, fabrica_de_teste, id_usuaria, id_recurso
):
    # O TestClient só devolve a resposta depois que tudo terminou, inclusive um
    # commit atrasado. Para ver o instante em que o 201 sai, o app vai embrulhado:
    # no http.response.start, outra conexão conta as reservas (ADR 0010, emenda
    # de 2026-10-27).
    # Preparar
    token = criar_access_token(id_usuaria, "usuario", datetime.now(UTC))
    cabecalho = {"Authorization": f"Bearer {token}"}
    corpo = {
        "id_recurso": id_recurso,
        "convidados": 4,
        "inicio": "2026-10-01T15:00:00Z",
        "fim": "2026-10-01T16:00:00Z",
    }
    vistas_no_201: list[int] = []

    async def app_que_espia(scope, receive, send):
        async def send_que_espia(mensagem):
            if mensagem["type"] == "http.response.start":
                with fabrica_de_teste() as outra_conexao:
                    contagem = select(func.count()).select_from(Reserva)
                    vistas_no_201.append(outra_conexao.scalar(contagem))
            await send(mensagem)

        await app(scope, receive, send_que_espia)

    cliente = TestClient(app_que_espia, base_url="https://testserver/api")

    # Agir
    resposta = cliente.post("/reservas", json=corpo, headers=cabecalho)

    # Conferir
    assert resposta.status_code == 201
    assert vistas_no_201 == [1]


def esperar_alguem_travado(fabrica_de_teste):
    # Pergunta ao Postgres, por uma terceira conexão, se alguma transação está
    # esperando outra terminar (wait_event 'transactionid'). Devolve quando vê.
    consulta = text(
        "SELECT count(*) FROM pg_stat_activity"
        " WHERE datname = current_database()"
        " AND wait_event_type = 'Lock' AND wait_event = 'transactionid'"
    )
    limite = monotonic() + PRAZO
    while monotonic() < limite:
        with fabrica_de_teste() as observadora:
            if observadora.scalar(consulta) == 1:
                return
        sleep(0.01)
    raise AssertionError("a API nunca ficou esperando a outra transação")


@pytest.mark.concorrencia
def test_deadlock_na_exclude_devolve_409(
    api_com_sessao_real, fabrica_de_teste, id_usuaria, id_recurso
):
    # O deadlock da emenda de 2026-10-27 ao ADR 0014, montado de propósito:
    #   A 15h-16h (o teste, sem comitar)
    #   B 15h30-16h30 (a API): sobrepõe A -> espera o teste
    #   C 16h-17h (o teste): sobrepõe B, encosta em A -> espera a API
    # Cada uma espera a outra. A API começou a esperar primeiro, então o
    # deadlock_timeout dela vence primeiro, e o Postgres a aborta com 40P01.
    # Preparar
    token = criar_access_token(id_usuaria, "usuario", datetime.now(UTC))
    cabecalho = {"Authorization": f"Bearer {token}"}
    corpo_b = {
        "id_recurso": id_recurso,
        "convidados": 4,
        "inicio": "2026-10-01T15:30:00Z",
        "fim": "2026-10-01T16:30:00Z",
    }
    status: list[int] = []

    def reservar_b():
        cliente = TestClient(
            app, base_url="https://testserver/api", raise_server_exceptions=False
        )
        resposta = cliente.post("/reservas", json=corpo_b, headers=cabecalho)
        status.append(resposta.status_code)

    def reserva(inicio_h, inicio_m, fim_h, fim_m):
        return Reserva(
            id_usuario=id_usuaria,
            id_recurso=id_recurso,
            convidados=4,
            periodo=Range(
                datetime(2026, 10, 1, inicio_h, inicio_m, tzinfo=UTC),
                datetime(2026, 10, 1, fim_h, fim_m, tzinfo=UTC),
                bounds="[)",
            ),
            status_reserva="confirmada",
        )

    thread = threading.Thread(target=reservar_b, daemon=True)

    # Agir
    with fabrica_de_teste() as teste:
        teste.add(reserva(15, 0, 16, 0))  # A
        teste.flush()
        thread.start()
        esperar_alguem_travado(fabrica_de_teste)
        teste.add(reserva(16, 0, 17, 0))  # C: fecha o círculo
        teste.flush()
    thread.join(timeout=PRAZO)

    # Conferir
    assert not thread.is_alive(), "a thread pendurou"
    assert status == [409]
