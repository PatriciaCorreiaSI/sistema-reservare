SENHA = "senha123"  # a mesma que gerou SENHA_HASH no conftest


def test_criar_usuario_sem_ser_admin_devolve_403(client, usuario):
    # Prepara login do usuário e guarda o access_token da resposta:
    # A Ana (fixture, usuário comum) entra e recebe o access token.
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    access_token = resposta.json()["access_token"]

    # Agir: com o token dela, tentar cadastrar alguém. Corpo válido, para que
    # a única razão da recusa seja o privilégio.
    novo_usuario = {
        "nome_usuario": "Felipe",
        "email_usuario": "felipe@teste.com",
        "senha": "senha456",
        "privilegio_usuario": "usuario",
    }
    resposta = client.post(
        "/usuarios",
        json=novo_usuario,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Conferir
    assert resposta.status_code == 403


def test_criar_usuario_com_email_existente_devolve_409(client, admin, usuario):
    # Preparar
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": admin.email_usuario, "senha": SENHA},
    )
    access_token = resposta.json()["access_token"]

    # Agir
    novo_usuario = {
        "nome_usuario": "Anamaria",
        "email_usuario": usuario.email_usuario,
        "senha": "senha456",
        "privilegio_usuario": "usuario",
    }
    resposta = client.post(
        "/usuarios",
        json=novo_usuario,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Conferir
    assert resposta.status_code == 409
