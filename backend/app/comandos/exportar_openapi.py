import json
from pathlib import Path

from app.main import app


def exportar(destino: Path) -> None:
    """Grava o contrato OpenAPI do app em destino, como JSON legível e com LF.

    Não lê ambiente nem decide o caminho: quem decide é o main().
    """
    contrato = app.openapi()
    texto = json.dumps(contrato, indent=2, ensure_ascii=False) + "\n"
    destino.write_text(texto, encoding="utf-8", newline="\n")


def main() -> None:
    """Calcula frontend/openapi.json a partir da raiz do repositório e
    chama exportar.
    """
    raiz = Path(__file__).resolve().parents[3]
    destino = raiz / "frontend" / "openapi.json"
    exportar(destino)
    print(f"Contrato gravado em {destino}")


if __name__ == "__main__":
    main()
