import pytest


@pytest.mark.concorrencia
@pytest.mark.skip(
    reason="Etapa 4: fixtures que comitam ainda não desenhadas (ADR 0015)"
)
def test_reservas_simultaneas_no_mesmo_horario_devolvem_um_201_e_um_409():
    """Duas threads, cada uma com o seu TestClient, liberadas por um Barrier.
    O conjunto dos status é {201, 409}, sem depender de qual thread vence."""
