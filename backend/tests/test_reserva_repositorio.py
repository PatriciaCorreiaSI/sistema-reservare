import pytest

pendente = pytest.mark.skip(reason="ainda não escrito")


@pendente
def test_criar_com_recurso_inexistente_levanta_recurso_nao_encontrado(client, usuario):
    """ReservaRepository(sessao).criar(Reserva(...)) com todos os campos válidos
    menos id_recurso, que aponta para um recurso que não existe
    -> pytest.raises9RecursoNaoEncontrado)."""
