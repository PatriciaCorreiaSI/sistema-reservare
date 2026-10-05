import pytest

from app.security import validar_segredo


def test_segredo_com_31_bytes_e_recusado():
    # Um a menos que o mínimo -> ValueError.
    segredo = "x" * 31

    with pytest.raises(ValueError, match="32 bytes"):
        validar_segredo(segredo)


def test_segredo_com_32_bytes_e_aceito():
    # Exatamente o mínimo -> devolve o próprio segredo.
    segredo = "x" * 32
    assert validar_segredo(segredo) == segredo


def test_segredo_vazio_e_recusado():
    # Segredo vazio ("") -> ValueError. É o caso que os.environ[...] deixa passar.
    segredo = ""

    with pytest.raises(ValueError, match="32 bytes"):
        validar_segredo(segredo)


def test_tamanho_e_medido_em_bytes_nao_em_caracteres():
    # 16 caracteres "ç" = 32 bytes -> aceito.
    # Se a função medisse caracteres, recusaria.
    segredo = "ç" * 16
    assert validar_segredo(segredo) == segredo
