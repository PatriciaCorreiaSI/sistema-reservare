import pytest

from app.comandos.criar_admin import criar_admin
from app.security import hasher
from app.services.excecoes import EmailJaCadastrado

SENHA_ADMIN = "senha-do-admin"  # dado do teste; nada vem do .env


def test_criar_admin_grava_admin_ativo(sessao):
    # Preparar: nada, o banco vazio da fixture é o cenário.

    # Agir: a interface testada é a função, não uma rota. A sessão é a da fixture.
    criado = criar_admin(sessao, "Admin", "admin@teste.com", SENHA_ADMIN)

    # Conferir: é admin, está vivo, e a senha foi guardada com hash.
    assert criado.privilegio_usuario == "admin"
    assert criado.status_usuario == "ativo"
    assert criado.senha_usuario_hash != SENHA_ADMIN
    assert hasher.verify(SENHA_ADMIN, criado.senha_usuario_hash)


def test_criar_admin_com_email_existente_levanta_erro(sessao, admin):
    # Preparar: a fixture admin já gravou, o cenário está pronto
    # só por ela ter sido pedida

    # Agir e conferir: o with é o coferir; a chamada dentro dele é o agir.
    # Nomeados, para o e-mail não cair no lugar de outro str.
    with pytest.raises(EmailJaCadastrado):
        criar_admin(
            sessao,
            nome="Admin_02",
            email=admin.email_usuario,
            senha=SENHA_ADMIN,
        )
