import threading
from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.db import obter_sessao
from app.dependencies import obter_agora, obter_fuso
from app.main import app
from app.models import Recurso, Usuario
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
    cliente = TestClient(app)
    barreira.wait()
    resposta = cliente.post("/reservas", json=corpo, headers=cabecalho)
    status.append(resposta.status_code)


@pytest.mark.concorrencia
def test_reservas_simultaneas_no_mesmo_horario_devolvem_um_201_e_um_409(
    api_com_sessao_real, id_usuaria, id_recurso
):
    """Duas threads, cada uma com o seu TestClient, liberadas por um Barrier.
    O conjunto dos status é {201, 409}, sem depender de qual thread vence."""
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
