import json
import logging
import re

import pytest
from asgi_correlation_id import correlation_id
from fastapi.testclient import TestClient
from pythonjsonlogger.json import JsonFormatter

from app.db import obter_sessao
from app.logging_config import configurar_logs
from app.main import app

FORMATO_DO_ID = r"[0-9a-f]{32}"
ID_VALIDO = "0123456789abcdef0123456789abcdef"


def test_resposta_traz_x_request_id(client):
    resposta = client.get("https://testserver/health")
    assert resposta.status_code == 200
    assert re.fullmatch(FORMATO_DO_ID, resposta.headers["X-Request-ID"])


def test_x_request_id_valido_volta_igual(client):
    resposta = client.get(
        "https://testserver/health", headers={"X-Request-ID": ID_VALIDO}
    )
    assert resposta.status_code == 200
    assert resposta.headers["X-Request-ID"] == ID_VALIDO


def test_x_request_id_invalido_e_trocado(client):
    resposta = client.get(
        "https://testserver/health", headers={"X-Request-ID": "abc falso"}
    )
    assert resposta.status_code == 200
    assert resposta.headers["X-Request-ID"] != "abc falso"
    assert re.fullmatch(FORMATO_DO_ID, resposta.headers["X-Request-ID"])


@pytest.fixture
def client_sem_relancar(client):
    return TestClient(
        app, base_url="https://testserver/api", raise_server_exceptions=False
    )


def sessao_que_falha():
    raise RuntimeError("falha de propósito")


def test_erro_nao_tratado_responde_500_com_x_request_id(client_sem_relancar):
    app.dependency_overrides[obter_sessao] = sessao_que_falha
    resposta = client_sem_relancar.post(
        "/auth/login",
        json={"email_usuario": "ana@exemplo.com", "senha": "senha456"},
    )
    assert resposta.status_code == 500
    assert resposta.json() == {"detail": "Erro interno"}
    assert re.fullmatch(FORMATO_DO_ID, resposta.headers["X-Request-ID"])


def handler_json() -> logging.Handler:
    return next(
        handler
        for handler in logging.getLogger().handlers
        if isinstance(handler.formatter, JsonFormatter)
    )


def test_linha_de_log_sai_em_json_com_o_request_id():
    configurar_logs()
    token = correlation_id.set(ID_VALIDO)
    try:
        registro = logging.LogRecord(
            "app.teste", logging.WARNING, __file__, 1, "olá", None, None
        )
        saida = handler_json()
        saida.filter(registro)
        linha = json.loads(saida.format(registro))
    finally:
        correlation_id.reset(token)

    assert linha["level"] == "WARNING"
    assert linha["logger"] == "app.teste"
    assert linha["message"] == "olá"
    assert linha["request_id"] == ID_VALIDO
    assert linha["timestamp"].endswith("+00:00")
