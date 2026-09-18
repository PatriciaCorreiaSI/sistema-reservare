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
