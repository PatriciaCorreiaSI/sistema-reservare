import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.models import RefreshToken
from app.security import criar_access_token, hash_refresh_token

SENHA = "senha123"  # a mesma que gerou SENHA_HASH no conftest

pendente = pytest.mark.skip(reason="ainda não escrito")


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


def test_login_com_senha_errada_devolve_401(client, usuario):
    # POST /auth/login com e-mail da Ana e senha diferente de SENHA -> 401.
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": "senha-errada"},
    )
    assert resposta.status_code == 401


def test_login_com_email_inexistente_devolve_401(client):
    # POST /auth/login com e-mail que nenhum usuário tem -> 401.
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": "inexistente@teste.com", "senha": SENHA},
    )
    assert resposta.status_code == 401


def test_login_de_usuario_inativo_devolve_401(client, sessao, usuario):
    # Preparar: usuario.status_usuario = "inativo". sessao.commit().
    # Login com e-mail e senha certos -> 401.
    usuario.status_usuario = "inativo"
    sessao.commit()

    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    assert resposta.status_code == 401


def test_refresh_desconhecido_devolve_401(client):
    # POST /auth/refresh com um texto que nunca foi emitido -> 401.
    refresh = "refresh_token_desconhecido"
    resposta = client.post("/auth/refresh", json={"refresh_token": refresh})
    # Conferir
    assert resposta.status_code == 401


def test_refresh_vencido_devolve_401(client, sessao, usuario):
    # Preparar pelo modelo: RefreshToken da Ana com hash_token =
    # hash_refresh_token("refresh-vencido") e criado_em/expira_em no passado.
    # POST /auth/refresh com "refresh-vencido"-> 401.
    sessao.add(
        RefreshToken(
            id_usuario=usuario.id_usuario,
            hash_token=hash_refresh_token("refresh-vencido"),
            familia_token=uuid.uuid4(),
            criado_em=datetime(2020, 1, 1, tzinfo=UTC),
            expira_em=datetime(2020, 1, 8, tzinfo=UTC),
        )
    )
    sessao.commit()
    resposta = client.post("/auth/refresh", json={"refresh_token": "refresh-vencido"})
    assert resposta.status_code == 401


def test_refresh_de_usuario_inativo_devolve_401(client, sessao, usuario):
    # Preparar: login (assert 200), depois usuario.status_usuario = "inativo";
    # sessao.commit(). Refresh com o token do login -> 401.
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    assert resposta.status_code == 200

    usuario.status_usuario = "inativo"
    sessao.commit()

    refresh = resposta.json()["refresh_token"]
    resposta = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert resposta.status_code == 401


def test_access_assinado_com_outra_chave_devolve_401(client, usuario):
    # GET /recursos com um JWT feito por jwt.encode com outra chave (32+ bytes)
    # -> 401, com WWW-Authenticate: Bearer.
    # Preparar: um token igual ao verdadeiro em tudo, menos na chave que o assinou.
    payload = {
        "sub": str(usuario.id_usuario),
        "exp": datetime.now(UTC) + timedelta(minutes=15),
        "privilegio_usuario": usuario.privilegio_usuario,
    }
    token = jwt.encode(
        payload, "chave-falsa-de-quem-quer-se-passar-pela-ana", algorithm="HS256"
    )
    resposta = client.get("/recursos", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401
    assert resposta.headers["WWW-Authenticate"] == "Bearer"


def test_access_vencido_devolve_401(client, usuario):
    # GET /recursos com criar_access_token(..., agora=um instante de 2020)
    # -> 401.
    token = criar_access_token(
        usuario.id_usuario,
        usuario.privilegio_usuario,
        datetime(2020, 1, 1, tzinfo=UTC),
    )
    resposta = client.get("/recursos", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401
    assert resposta.headers["WWW-Authenticate"] == "Bearer"
