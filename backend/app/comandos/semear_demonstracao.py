import os
from datetime import UTC, datetime, time, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.db import FabricaDeSessao
from app.dependencies import UsuarioAtual, obter_fuso
from app.models import Recurso, Usuario
from app.repositories.recurso import RecursoRepository
from app.repositories.reserva import ReservaRepository
from app.repositories.usuario import UsuarioRepository
from app.schemas.recurso import RecursoCriar
from app.schemas.reserva import ReservaCriar
from app.schemas.usuario import UsuarioCriar
from app.services.recurso import RecursoService
from app.services.reserva import ReservaService
from app.services.usuario import UsuarioService

SENHA_DE_DEMONSTRACAO = "demonstracao"

USUARIOS_DE_DEMONSTRACAO = [
    ("Ana Demonstração", "ana@reservare.example"),
    ("Bruno Demonstração", "bruno@reservare.example"),
]

RECURSOS_DE_DEMONSTRACAO = [
    RecursoCriar(
        nome_recurso="Sala de Reunião",
        ocupacao=8,
        hora_func_inicio=time(8),
        hora_func_fim=time(18),
    ),
    RecursoCriar(
        nome_recurso="Auditório",
        ocupacao=40,
        hora_func_inicio=time(8),
        hora_func_fim=time(18),
    ),
    RecursoCriar(
        nome_recurso="Projetor",
        ocupacao=1,
        hora_func_inicio=time(8),
        hora_func_fim=time(18),
    ),
]


def demonstracao_ligada() -> bool:
    """True só com DEMONSTRACAO == "1". Ausente, vazia, "0", "false": False."""
    return os.environ.get("DEMONSTRACAO") == "1"


def garantir_usuario(
    sessao: Session,
    nome: str,
    email: str,
    senha: str,
    privilegio: Literal["admin", "usuario"],
) -> Usuario:
    """Busca pelo e-mail; se existe, devolve sem mexer. Senão, cria pelo
    UsuarioService (validação do UsuarioCriar e Argon2 incluídos)."""
    existente = UsuarioRepository(sessao).buscar_por_email(email)
    if existente is not None:
        return existente
    dados = UsuarioCriar(
        nome_usuario=nome,
        email_usuario=email,
        senha=senha,
        privilegio_usuario=privilegio,
    )
    return UsuarioService(sessao).criar(dados)


def garantir_recurso(sessao: Session, dados: RecursoCriar) -> Recurso:
    """Busca pelo nome (buscar_por_nome); se existe, devolve sem mexer.
    Senão, cria pelo RecursoService."""
    existente = RecursoRepository(sessao).buscar_por_nome(dados.nome_recurso)
    if existente is not None:
        return existente
    return RecursoService(sessao).criar(dados)


def recriar_reservas(
    sessao: Session,
    agora: datetime,
    fuso: ZoneInfo,
    ana: Usuario,
    bruno: Usuario,
    recursos: dict[str, Recurso],
) -> None:
    """Apaga as reservas de ana e bruno e grava as seis do conjunto, com
    D = agora.astimezone(fuso).date(). Futuras: ReservaService com o agora real.
    Histórico: ReservaService com agora - 3 dias; a cancelada do Bruno é criada
    e cancelada nesse service, antes da concluída da Ana no mesmo horário.
    recursos é indexado por nome_recurso."""
    ReservaRepository(sessao).apagar_dos_usuarios([ana.id_usuario, bruno.id_usuario])

    hoje = agora.astimezone(fuso).date()
    presente = ReservaService(sessao, agora=agora, fuso=fuso)
    passado = ReservaService(sessao, agora=agora - timedelta(days=3), fuso=fuso)

    def como(usuario: Usuario) -> UsuarioAtual:
        return UsuarioAtual(id_usuario=usuario.id_usuario, privilegio_usuario="usuario")

    def pedido(nome_recurso: str, dias: int, inicio: time, fim: time) -> ReservaCriar:
        dia = hoje + timedelta(days=dias)
        return ReservaCriar(
            id_recurso=recursos[nome_recurso].id_recurso,
            convidados=1,
            inicio=datetime.combine(dia, inicio, tzinfo=fuso),
            fim=datetime.combine(dia, fim, tzinfo=fuso),
        )

    cancelada = passado.criar(
        pedido("Sala de Reunião", -1, time(10), time(11)), como(bruno)
    )
    passado.cancelar(cancelada.id_reserva, como(bruno))
    passado.criar(pedido("Sala de Reunião", -1, time(10), time(11)), como(ana))
    passado.criar(pedido("Auditório", -2, time(14), time(16)), como(bruno))

    presente.criar(pedido("Sala de Reunião", 1, time(10), time(11)), como(ana))
    presente.criar(pedido("Projetor", 2, time(9), time(12)), como(ana))
    presente.criar(pedido("Auditório", 1, time(14), time(16)), como(bruno))


def semear(
    sessao: Session,
    agora: datetime,
    fuso: ZoneInfo,
    admin_nome: str,
    admin_email: str,
    admin_senha: str,
) -> None:
    """garantir_usuario do admin e dos dois usuários, garantir_recurso dos
    três, recriar_reservas. Não lê ambiente, não abre sessão, não comita."""
    garantir_usuario(sessao, admin_nome, admin_email, admin_senha, "admin")
    ana, bruno = [
        garantir_usuario(sessao, nome, email, SENHA_DE_DEMONSTRACAO, "usuario")
        for nome, email in USUARIOS_DE_DEMONSTRACAO
    ]
    recursos = {
        dados.nome_recurso: garantir_recurso(sessao, dados)
        for dados in RECURSOS_DE_DEMONSTRACAO
    }
    recriar_reservas(sessao, agora, fuso, ana, bruno, recursos)


def main() -> None:
    """Se não demonstracao_ligada(): imprime que pulou e retorna (código 0,
    a partida segue). Senão lê ADMIN_NOME, ADMIN_EMAIL, ADMIN_SENHA e o fuso
    (obter_fuso), abre `with FabricaDeSessao() as sessao, sessao.begin():`
    e chama semear com datetime.now(UTC)."""
    if not demonstracao_ligada():
        print("Semeadura pulada: DEMONSTRACAO não é 1.")
        return

    nome = os.environ["ADMIN_NOME"]
    email = os.environ["ADMIN_EMAIL"]
    senha = os.environ["ADMIN_SENHA"]

    with FabricaDeSessao() as sessao, sessao.begin():
        semear(sessao, datetime.now(UTC), obter_fuso(), nome, email, senha)

    # Só aqui o commit já aconteceu: agora é verdade que a demonstração existe.
    print("Demonstração semeada.")


if __name__ == "__main__":
    main()
