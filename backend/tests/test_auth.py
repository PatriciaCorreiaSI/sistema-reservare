SENHA = "senha123"  # a mesma que gerou SENHA_HASH no conftest


def test_refresh_apos_logout_devolve_401(client, usuario):
    # Preparar: entra. O e-mail vem da fixture; a senha é a conhecida.
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    refresh = resposta.json()["refresh_token"]

    # Preparar: sair, mandando o refresh que o login devolveu.
    client.post("/auth/logout", json={"refresh_token": refresh})

    # Agir: tentar renovar o refresh que acabou de ser revogado.
    resposta = client.post("/auth/refresh", json={"refresh_token": refresh})

    # Conferir
    assert resposta.status_code == 401


def test_login_com_credenciais_validas_devolve_200(client, usuario):
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["access_token"]
    assert corpo["refresh_token"]


def test_refresh_devolve_200_com_refresh_novo(client, usuario):
    # Preparar
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    refresh_r1 = resposta.json()["refresh_token"]

    # Agir
    resposta = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_r1},
    )

    # Conferir
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["refresh_token"] != refresh_r1


def test_refresh_reusado_devolve_401_e_revoga_familia(client, usuario):
    # Preparar: login(r1) → e uma rotação normal (r1 → r2).
    # r1 fica revogado pelo uso; r2 fica vivo → é ele que o reuso deve derrubar.
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    refresh_r1 = resposta.json()["refresh_token"]
    resposta = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_r1},
    )
    refresh_r2 = resposta.json()["refresh_token"]

    # Agir: alguém reapresenta r1 já revogado. Isso é o reuso
    resposta = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_r1},
    )

    # Conferir: o reuso é recusado...
    assert resposta.status_code == 401

    # ...e a família inteira cai, ou seja, refresh_r1
    # está revogado e refresh_r2 também não vale mais
    # Verificado pela interface (o que o cliente vê), não pela coluna revogado_em.
    resposta = client.post("/auth/refresh", json={"refresh_token": refresh_r2})
    assert resposta.status_code == 401
