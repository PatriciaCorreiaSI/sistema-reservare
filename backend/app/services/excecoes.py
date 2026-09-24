class ErroDeDominio(Exception):
    """Base de toda exceção de domínio."""


class RecursoNaoEncontrado(ErroDeDominio):
    pass


class RecursoEmUso(ErroDeDominio):
    pass


class CredenciaisInvalidas(ErroDeDominio):
    """Login ou refresh recusado.

    Uma exceção só para e-mail inexistente; senha errada; usuário inativo;
    refresh inválido, expirado ou reutilizado; access ausente, malformado
    ou expirado para a resposta não revelar qual dos casos aconteceu
    (api.md: a API não serve de lista de quem existe).
    """


class EmailJaCadastrado(ErroDeDominio):
    """POST /usuarios com e-mail que já existe.

    Vem do UNIQUE de usuario.email_usuario, que recusa a linha no flush;
    o UsuarioService traduz o IntegrityError nesta exceção e o main.py a
    devolve como 409.
    """


class PrivilegioInsuficiente(ErroDeDominio):
    """Privilégio insuficiente.

    Nasce no `exigir_admin` e vira `403`.
    """


class ReservaNaoEncontrada(ErroDeDominio):
    """Reserva inexistente ou de outra pessoa (ADR 0017).

    As duas levantam esta mesma exceção, e o main.py a devolve como 404:
    a resposta não revela que a reserva existe.
    """


class HorarioOcupado(ErroDeDominio):
    """Violação da `ex_reserva_sem_sobreposicao`.

    O ReservaRepository traduz o IntegrityError nesta exceção pelo nome da
    constraint (ADR 0014), e o main.py a devolve como 409.
    """


class RecursoInativo(ErroDeDominio):
    """Reserva pedida para um recurso inativo. Vira 409."""


class ReservaNaoCancelavel(ErroDeDominio):
    """Cancelar reserva já cancelada ou já terminada (ADR 0016).

    O UPDATE condicional afetou 0 linhas. Vira 409.
    """


class RegraDeReservaViolada(ErroDeDominio):
    """Mãe dos 422 que nascem no service.

    Um handler só, registrado para ela, atende todas as filhas; a mensagem
    vem do atributo `detalhe` de cada uma.
    """

    detalhe = "Regra de reserva violada"


class ReservaNoPassado(RegraDeReservaViolada):
    detalhe = "A reserva não pode começar no passado"


class ForaDoHorario(RegraDeReservaViolada):
    detalhe = "A reserva precisa caber no horário de funcionamento do recurso"


class ConvidadosAcimaDaOcupacao(RegraDeReservaViolada):
    detalhe = "Convidados acima da ocupação do recurso"
