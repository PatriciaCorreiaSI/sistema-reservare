from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import Range

from app.comandos.semear_demonstracao import (
    RECURSOS_DE_DEMONSTRACAO,
    USUARIOS_DE_DEMONSTRACAO,
    demonstracao_ligada,
    garantir_recurso,
    main,
    semear,
)
from app.models import Recurso, Reserva, Usuario
from app.schemas.recurso import RecursoCriar
from app.services.reserva import status_efetivo

AGORA = datetime(2026, 10, 1, 12, 0, tzinfo=UTC)  # D = 1/10 em São Paulo
FUSO = ZoneInfo("America/Sao_Paulo")
ADMIN_EMAIL = "admin@reservare.example"
EMAILS_DA_DEMONSTRACAO = [email for _, email in USUARIOS_DE_DEMONSTRACAO]


def semear_no_teste(sessao):
    semear(sessao, AGORA, FUSO, "Admin", ADMIN_EMAIL, "senha-do-admin")


def reservas_da_demonstracao(sessao):
    consulta = (
        select(Reserva, Usuario.email_usuario)
        .join(Usuario, Reserva.id_usuario == Usuario.id_usuario)
        .where(Usuario.email_usuario.in_(EMAILS_DA_DEMONSTRACAO))
    )
    return sessao.execute(consulta).all()


def contar(sessao, modelo):
    return sessao.scalar(select(func.count()).select_from(modelo))


def test_demonstracao_ligada_com_1(monkeypatch):
    """DEMONSTRACAO="1" (monkeypatch) → True."""
    monkeypatch.setenv("DEMONSTRACAO", "1")

    assert demonstracao_ligada() is True


def test_demonstracao_desligada_sem_a_variavel(monkeypatch):
    """delenv → False."""
    monkeypatch.delenv("DEMONSTRACAO", raising=False)

    assert demonstracao_ligada() is False


@pytest.mark.parametrize("valor", ["", "0", "false", "sim"])
def test_demonstracao_desligada_com_outro_valor(monkeypatch, valor):
    """DEMONSTRACAO=valor → False."""
    monkeypatch.setenv("DEMONSTRACAO", valor)

    assert demonstracao_ligada() is False


def test_semear_cria_admin_usuarios_e_recursos(sessao):
    semear_no_teste(sessao)

    admin = sessao.scalar(select(Usuario).where(Usuario.email_usuario == ADMIN_EMAIL))
    assert admin is not None
    assert admin.privilegio_usuario == "admin"
    emails = sessao.scalars(select(Usuario.email_usuario)).all()
    for email in EMAILS_DA_DEMONSTRACAO:
        assert email in emails
    nomes = sessao.scalars(select(Recurso.nome_recurso)).all()
    for dados in RECURSOS_DE_DEMONSTRACAO:
        assert dados.nome_recurso in nomes


def test_semear_duas_vezes_nao_duplica(sessao):
    """semear duas vezes: mesma contagem de usuários, de recursos e
    seis reservas das duas contas de demonstração."""
    semear_no_teste(sessao)
    usuarios_depois_da_primeira = contar(sessao, Usuario)
    recursos_depois_da_primeira = contar(sessao, Recurso)

    semear_no_teste(sessao)

    assert contar(sessao, Usuario) == usuarios_depois_da_primeira
    assert contar(sessao, Recurso) == recursos_depois_da_primeira
    assert len(reservas_da_demonstracao(sessao)) == 6


def test_semear_apaga_a_reserva_feita_por_visitante(sessao):
    """semear; grava uma reserva extra da Ana; semear de novo → a extra sumiu."""
    semear_no_teste(sessao)
    ana = sessao.scalar(
        select(Usuario).where(Usuario.email_usuario == EMAILS_DA_DEMONSTRACAO[0])
    )
    projetor = sessao.scalar(select(Recurso).where(Recurso.nome_recurso == "Projetor"))
    extra = Reserva(
        id_usuario=ana.id_usuario,
        id_recurso=projetor.id_recurso,
        convidados=1,
        periodo=Range(
            datetime(2026, 10, 5, 13, 0, tzinfo=UTC),
            datetime(2026, 10, 5, 14, 0, tzinfo=UTC),
            bounds="[)",
        ),
        status_reserva="confirmada",
    )
    sessao.add(extra)
    sessao.commit()
    id_extra = extra.id_reserva

    semear_no_teste(sessao)

    ids = [reserva.id_reserva for reserva, _ in reservas_da_demonstracao(sessao)]
    assert id_extra not in ids


def test_semear_preserva_reserva_de_quem_nao_e_de_demonstracao(sessao, usuario):
    """Reserva da fixture usuario (ana@teste.com) gravada antes; semear →
    ela continua lá. É o primeiro 'Como eu saberia que errei' do ADR."""
    sala = Recurso(
        nome_recurso="Sala da Fixture",
        ocupacao=4,
        hora_func_inicio=time(8),
        hora_func_fim=time(18),
        status_recurso="ativo",
    )
    sessao.add(sala)
    sessao.commit()
    reserva = Reserva(
        id_usuario=usuario.id_usuario,
        id_recurso=sala.id_recurso,
        convidados=1,
        periodo=Range(
            datetime(2026, 10, 2, 13, 0, tzinfo=UTC),
            datetime(2026, 10, 2, 14, 0, tzinfo=UTC),
            bounds="[)",
        ),
        status_reserva="confirmada",
    )
    sessao.add(reserva)
    sessao.commit()
    id_reserva = reserva.id_reserva

    semear_no_teste(sessao)

    assert sessao.get(Reserva, id_reserva) is not None


def test_semear_cria_os_tres_estados(sessao):
    """status_efetivo(reserva, AGORA) das seis: Bruno tem cancelada e concluída;
    Ana tem concluída e confirmadas."""
    semear_no_teste(sessao)

    estados: dict[str, list[str]] = {email: [] for email in EMAILS_DA_DEMONSTRACAO}
    for reserva, email in reservas_da_demonstracao(sessao):
        estados[email].append(status_efetivo(reserva, AGORA))
    ana, bruno = EMAILS_DA_DEMONSTRACAO
    assert sorted(estados[ana]) == ["concluida", "confirmada", "confirmada"]
    assert sorted(estados[bruno]) == ["cancelada", "concluida", "confirmada"]


def test_garantir_recurso_com_nome_repetido_usa_o_de_menor_id(sessao):
    """Dois recursos 'Projetor' gravados pelo modelo; garantir_recurso
    devolve o de menor id_recurso e não cria um terceiro."""
    primeiro = Recurso(
        nome_recurso="Projetor",
        ocupacao=1,
        hora_func_inicio=time(8),
        hora_func_fim=time(18),
        status_recurso="ativo",
    )
    segundo = Recurso(
        nome_recurso="Projetor",
        ocupacao=1,
        hora_func_inicio=time(8),
        hora_func_fim=time(18),
        status_recurso="ativo",
    )
    sessao.add(primeiro)
    sessao.commit()
    sessao.add(segundo)
    sessao.commit()

    devolvido = garantir_recurso(
        sessao,
        RecursoCriar(
            nome_recurso="Projetor",
            ocupacao=1,
            hora_func_inicio=time(8),
            hora_func_fim=time(18),
        ),
    )

    assert devolvido.id_recurso == primeiro.id_recurso
    projetores = sessao.scalars(
        select(Recurso).where(Recurso.nome_recurso == "Projetor")
    ).all()
    assert len(projetores) == 2


def test_main_desligada_nao_le_o_ambiente_nem_semeia(monkeypatch):
    """DEMONSTRACAO="0" e as três ADMIN_* apagadas (delenv): main() termina
    sem erro. Sem a guarda, quebraria com keyError antes de abrir sessão."""
    monkeypatch.setenv("DEMONSTRACAO", "0")
    for nome in ["ADMIN_NOME", "ADMIN_EMAIL", "ADMIN_SENHA"]:
        monkeypatch.delenv(nome, raising=False)

    main()
