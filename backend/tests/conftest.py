import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import obter_sessao, url_do_ambiente
from app.main import app


@pytest.fixture(scope="session")
def url_de_teste():
    return url_do_ambiente().set(database="reservare_test")


@pytest.fixture(scope="session")
def engine_de_teste(url_de_teste):
    config = Config("alembic.ini")
    config.set_main_option(
        "sqlalchemy.url", url_de_teste.render_as_string(hide_password=False)
    )
    command.upgrade(config, "head")
    engine = create_engine(url_de_teste)
    yield engine
    engine.dispose()


@pytest.fixture
def sessao(engine_de_teste):
    conexao = engine_de_teste.connect()
    transacao = conexao.begin()
    sessao = Session(bind=conexao)
    yield sessao
    sessao.close()
    transacao.rollback()
    conexao.close()


@pytest.fixture
def client(sessao):
    def obter_sessao_de_teste():
        yield sessao

    app.dependency_overrides[obter_sessao] = obter_sessao_de_teste
    return TestClient(app)
    app.dependency_overrides.clear()
