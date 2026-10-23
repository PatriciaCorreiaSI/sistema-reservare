import pytest

from app.db import url_do_ambiente

URL_DO_NEON = "postgresql://ana:segredo@ep-exemplo.neon.tech/reservare?sslmode=require"


@pytest.fixture
def variaveis_derivadas(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_USER", "ana")
    monkeypatch.setenv("POSTGRES_PASSWORD", "segredo")
    monkeypatch.setenv("POSTGRES_DB", "banco_do_teste")
    monkeypatch.setenv("DB_HOST", "host-do-teste")


def test_url_pronta_troca_o_driver(monkeypatch, variaveis_derivadas):
    monkeypatch.setenv("DATABASE_URL", URL_DO_NEON)

    url = url_do_ambiente()

    assert url.drivername == "postgresql+psycopg"
    assert url.host == "ep-exemplo.neon.tech"
    assert url.database == "reservare"


def test_url_pronta_mantem_o_sslmode(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", URL_DO_NEON)

    url = url_do_ambiente()

    assert url.query["sslmode"] == "require"


def test_sem_url_pronta_deriva_das_variaveis(monkeypatch, variaveis_derivadas):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    url = url_do_ambiente()

    assert url.host == "host-do-teste"
    assert url.database == "banco_do_teste"


def test_url_pronta_vazia_deriva_das_variaveis(monkeypatch, variaveis_derivadas):
    monkeypatch.delenv("DATABASE_URL", "")

    url = url_do_ambiente()

    assert url.host == "host-do-teste"
    assert url.database == "banco_do_teste"
