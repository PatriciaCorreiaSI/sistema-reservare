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


def test_buscar_recurso_por_id(client):
    dados = {
        "nome_recurso": "Sala 1",
        "ocupacao": 10,
        "hora_func_inicio": "08:00:00",
        "hora_func_fim": "18:00:00",
    }
    criado = client.post("/recursos", json=dados).json()

    resposta = client.get(f"/recursos/{criado['id_recurso']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome_recurso"] == "Sala 1"


def test_listar_recurso(client):
    dados = {
        "nome_recurso": "Sala 1",
        "ocupacao": 10,
        "hora_func_inicio": "08:00:00",
        "hora_func_fim": "18:00:00",
    }
    criado = client.post("/recursos", json=dados).json()

    resposta = client.get("/recursos")

    assert resposta.status_code == 200
    ids = [r["id_recurso"] for r in resposta.json()]
    assert criado["id_recurso"] in ids


def test_atualizar_recurso(client):
    dados = {
        "nome_recurso": "Sala 1",
        "ocupacao": 10,
        "hora_func_inicio": "08:00:00",
        "hora_func_fim": "18:00:00",
    }
    criado = client.post("/recursos", json=dados).json()

    resposta = client.patch(
        f"/recursos/{criado['id_recurso']}", json={"status_recurso": "inativo"}
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["nome_recurso"] == "Sala 1"
    assert corpo["status_recurso"] == "inativo"


def test_remover_recurso(client):
    dados = {
        "nome_recurso": "Sala 1",
        "ocupacao": 10,
        "hora_func_inicio": "08:00:00",
        "hora_func_fim": "18:00:00",
    }
    criado = client.post("/recursos", json=dados).json()

    resposta = client.delete(f"/recursos/{criado['id_recurso']}")
    assert resposta.status_code == 204

    depois = client.get(f"recursos/{criado['id_recurso']}")
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


def test_criar_recurso_sem_campo_obrigatorio(client):
    resposta = client.post("/recursos", json={"nome_recurso": "Sala 1"})
    assert resposta.status_code == 422
