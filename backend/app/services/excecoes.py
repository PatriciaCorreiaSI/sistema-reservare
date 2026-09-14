class ErroDeDominio(Exception):
    """Base de toda exceção de domínio."""


class RecursoNaoEncontrado(ErroDeDominio):
    pass


class RecursoEmUso(ErroDeDominio):
    pass
