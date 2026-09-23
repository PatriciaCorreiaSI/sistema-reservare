import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import obter_sessao, url_do_ambiente
from app.main import app
from app.models import Usuario

hasher = PasswordHash.recommended()
SENHA_HASH = hasher.hash("senha123")


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
    sessao = Session(bind=conexao, join_transaction_mode="create_savepoint")
    yield sessao
    sessao.close()
    transacao.rollback()
    conexao.close()


@pytest.fixture
def client(sessao):
    # Substituta de obter_sessao (ADR 0011, emenda de 2026-09-23): repete o
    # ciclo de pp/db.py: commit se deu certo, rollback se uma exceção atravessou.
    # Com o create_savepoint, ambos agem só sobre o savepoint.
    # Sem criar nem fechar a sessão: isso é da fixture `sessao`.
    def obter_sessao_de_teste():
        try:
            yield sessao
            sessao.commit()
        except Exception:
            sessao.rollback()
            raise

    app.dependency_overrides[obter_sessao] = obter_sessao_de_teste
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def recurso_criado(client):
    dados = {
        "nome_recurso": "Sala 1",
        "ocupacao": 10,
        "hora_func_inicio": "08:00:00",
        "hora_func_fim": "18:00:00",
    }
    return client.post("/recursos", json=dados).json()


@pytest.fixture
def usuario(sessao):
    usuario = Usuario(
        privilegio_usuario="usuario",
        nome_usuario="Ana",
        email_usuario="ana@teste.com",
        senha_usuario_hash=SENHA_HASH,
        status_usuario="ativo",
    )
    sessao.add(usuario)
    sessao.flush()
    return usuario


@pytest.fixture
def admin(sessao):
    admin = Usuario(
        privilegio_usuario="admin",
        nome_usuario="João",
        email_usuario="joao@teste.com",
        senha_usuario_hash=SENHA_HASH,
        status_usuario="ativo",
    )
    sessao.add(admin)
    sessao.flush()
    return admin
