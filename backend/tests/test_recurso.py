from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import Range

from app.models import Reserva, Usuario


def test_health(client):
    resposta = client.get("/health")
    assert resposta.status_code == 200


def test_criar_recurso(client):
    dados = {
        "nome_recurso": "Sala 1",
        "ocupacao": 10,
        "hora_func_inicio": "08:00:00",
        "hora_func_fim": "18:00:00",
    }
    resposta = client.post("/recursos", json=dados)
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["nome_recurso"] == "Sala 1"
    assert corpo["status_recurso"] == "ativo"


def test_buscar_recurso_por_id(client, recurso_criado):
    resposta = client.get(f"/recursos/{recurso_criado['id_recurso']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome_recurso"] == "Sala 1"


def test_listar_recurso(client, recurso_criado):
    resposta = client.get("/recursos")

    assert resposta.status_code == 200
    ids = [r["id_recurso"] for r in resposta.json()]
    assert recurso_criado["id_recurso"] in ids


def test_atualizar_recurso(client, recurso_criado):
    resposta = client.patch(
        f"/recursos/{recurso_criado['id_recurso']}", json={"status_recurso": "inativo"}
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["nome_recurso"] == "Sala 1"
    assert corpo["status_recurso"] == "inativo"


def test_remover_recurso(client, recurso_criado):
    resposta = client.delete(f"/recursos/{recurso_criado['id_recurso']}")
    assert resposta.status_code == 204

    depois = client.get(f"recursos/{recurso_criado['id_recurso']}")
    assert depois.status_code == 404


def test_buscar_recurso_inexistente(client):
    resposta = client.get("recursos/999999")
    assert resposta.status_code == 404


def test_atualizar_recurso_inexistente(client):
    resposta = client.patch("recursos/999999", json={"status_recurso": "inativo"})
    assert resposta.status_code == 404


def test_remover_recurso_inexistente(client):
    resposta = client.delete("recursos/999999")
    assert resposta.status_code == 404


def test_remover_recurso_em_uso(client, sessao, recurso_criado):
    # Prepara recurso pela porta HTTP
    id_recurso = recurso_criado["id_recurso"]

    # Prepara usuário e reserva pela porta do banco de dados
    usuario = Usuario(
        privilegio_usuario="usuario",
        nome_usuario="Ana",
        email_usuario="ana@teste.com",
        senha_usuario_hash="hash-falso",
        status_usuario="ativo",
    )
    sessao.add(usuario)
    sessao.flush()

    periodo = Range(
        datetime(2026, 10, 1, 9, 0, tzinfo=UTC),
        datetime(2026, 10, 1, 10, 0, tzinfo=UTC),
        bounds="[)",
    )

    reserva = Reserva(
        id_usuario=usuario.id_usuario,
        id_recurso=id_recurso,
        convidados=7,
        periodo=periodo,
        status_reserva="confirmada",
    )
    sessao.add(reserva)
    sessao.flush()

    # Agir e conferir
    resposta = client.delete(f"/recursos/{id_recurso}")
    assert resposta.status_code == 409


def test_criar_recurso_sem_campo_obrigatorio(client):
    resposta = client.post("/recursos", json={"nome_recurso": "Sala 1"})
    assert resposta.status_code == 422
