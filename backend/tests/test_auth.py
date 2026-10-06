import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.models import RefreshToken
from app.security import REFRESH_DIAS, criar_access_token, hash_refresh_token

SENHA = "senha123"  # a mesma que gerou SENHA_HASH no conftest
COOKIE = "refresh_token"

pendente = pytest.mark.skip(reason="ainda não escrito")


def usar_refresh(client, valor):
    # O pote de cookies do TestClient guarda o que o servidor mandou, como um
    # navegador. Para reapresentar um valor específico (reuso, vencido,
    # e desconhecido), esvazia o pote e põe só ele: senão iriam os dois.
    client.cookies.clear()
    client.cookies.set(COOKIE, valor)


def test_refresh_apos_logout_devolve_401(client, usuario):
    # Preparar: entra. O e-mail vem da fixture; a senha é a conhecida.
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    assert resposta.status_code == 200
    refresh = resposta.cookies[COOKIE]

    # Preparar: sair. O pote manda o cookie; a resposta o apaga do pote.
    resposta = client.post("/auth/logout")
    assert resposta.status_code == 204

    # Agir: quem copiou o valor antes do logout reapresenta o refresh revogado.
    usar_refresh(client, refresh)
    resposta = client.post("/auth/refresh")

    # Conferir
    assert resposta.status_code == 401


def test_login_com_credenciais_validas_devolve_200(client, usuario):
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    assert resposta.status_code == 200
    assert resposta.json()["access_token"]
    assert resposta.cookies[COOKIE]


def test_login_nao_devolve_refresh_no_corpo(client, usuario):
    # ADR 0023: se o refresh aparecesse no JSON, o JavaScript o leria e o
    # ganho do HttpOnly acabaria.
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    assert resposta.status_code == 200
    assert "refresh_token" not in resposta.json()


def test_cookie_do_refresh_tem_os_atributos_do_adr_0023(client, usuario):
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    assert resposta.status_code == 200

    # O Set-Cookie cru, com os atributos; minúsculo porque a caixa é livre.
    set_cookie = resposta.headers["set-cookie"].lower()
    assert "httponly" in set_cookie
    assert "secure" in set_cookie
    assert "samesite=strict" in set_cookie
    assert "path=/api/auth" in set_cookie
    assert f"max-age={REFRESH_DIAS * 24 * 60 * 60}" in set_cookie


def test_refresh_devolve_200_com_refresh_novo(client, usuario):
    # Preparar
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    assert resposta.status_code == 200
    refresh_r1 = resposta.cookies[COOKIE]

    # Agir: sem corpo; o pote manda o cookie do login.
    resposta = client.post("/auth/refresh")

    # Conferir: rotação → o cookie novo é outro valor
    assert resposta.status_code == 200
    assert resposta.cookies[COOKIE] != refresh_r1


def test_refresh_reusado_devolve_401_e_revoga_familia(client, usuario):
    # Preparar: login(r1) → e uma rotação normal (r1 → r2).
    # r1 fica revogado pelo uso; r2 fica vivo → é ele que o reuso deve derrubar.
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    assert resposta.status_code == 200
    refresh_r1 = resposta.cookies[COOKIE]
    resposta = client.post("/auth/refresh")
    assert resposta.status_code == 200
    refresh_r2 = resposta.cookies[COOKIE]

    # Agir: alguém reapresenta r1 já revogado. Isso é o reuso
    usar_refresh(client, refresh_r1)
    resposta = client.post("/auth/refresh")

    # Conferir: o reuso é recusado...
    assert resposta.status_code == 401

    # ...e a família inteira cai, ou seja, refresh_r1
    # está revogado e refresh_r2 também não vale mais
    # Verificado pela interface (o que o cliente vê), não pela coluna revogado_em.
    usar_refresh(client, refresh_r2)
    resposta = client.post("/auth/refresh")
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


def test_refresh_sem_cookie_devolve_401(client):
    # Pedido sem cookie nenhum: sem credencial, não pedido mal formado
    resposta = client.post("/auth/refresh")
    assert resposta.status_code == 401
    assert resposta.headers["WWW-Authenticate"] == "Bearer"


def test_refresh_desconhecido_devolve_401(client):
    # POST /auth/refresh com um texto que nunca foi emitido -> 401.
    usar_refresh(client, "refresh_token_desconhecido")
    resposta = client.post("/auth/refresh")
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
    usar_refresh(client, "refresh-vencido")
    resposta = client.post("/auth/refresh")
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

    resposta = client.post("/auth/refresh")
    assert resposta.status_code == 401


def test_logout_apaga_o_cookie(client, usuario):
    # Preparar: entra; o pote guarda o cookie
    resposta = client.post(
        "/auth/login",
        json={"email_usuario": usuario.email_usuario, "senha": SENHA},
    )
    assert resposta.status_code == 200
    assert COOKIE in client.cookies

    # Agir
    resposta = client.post("/auth/logout")

    # Conferir: Max-Age=0 é a ordem de apagar. o pote obedece como um navegador
    assert resposta.status_code == 204
    assert COOKIE not in client.cookies


def test_logout_sem_cookie_devolve_204(client):
    # Idempotente: não há o que revogar, e o objetivo já está etingido
    resposta = client.post("auth/logout")
    assert resposta.status_code == 204


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
