import json
from pathlib import Path

from app.comandos.exportar_openapi import exportar


def test_exportar_grava_o_contrato_com_as_rotas_da_api(tmp_path: Path) -> None:
    destino = tmp_path / "openapi.json"

    exportar(destino)

    dados = json.loads(destino.read_text(encoding="utf-8"))
    assert "/api/auth/login" in dados["paths"]
