import logging
import os
import sys

from asgi_correlation_id import CorrelationIdFilter
from pythonjsonlogger.core import RESERVED_ATTRS
from pythonjsonlogger.json import JsonFormatter

LOGGERS_DO_UVICORN = ("uvicorn", "uvicorn.error", "uvicorn.access")


def configurar_logs() -> None:
    nivel = os.environ["LOG_NIVEL"]

    formatador = JsonFormatter(
        ["levelname", "name", "message", "correlation_id"],
        rename_fields={
            "levelname": "level",
            "name": "logger",
            "correlation_id": "request_id",
        },
        reserved_attrs=[*RESERVED_ATTRS, "color_message"],
        timestamp=True,
        json_ensure_ascii=False,
    )

    saida = logging.StreamHandler(sys.stdout)
    saida.addFilter(CorrelationIdFilter())
    saida.setFormatter(formatador)

    raiz = logging.getLogger()
    raiz.handlers.clear()
    raiz.addHandler(saida)
    raiz.setLevel(nivel)

    for nome in LOGGERS_DO_UVICORN:
        logger = logging.getLogger(nome)
        logger.handlers.clear()
        logger.propagate = True
