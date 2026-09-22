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
