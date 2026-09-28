from fastapi import APIRouter, Depends

from app.dependencies import UsuarioAtual, obter_usuario_atual
from app.schemas.reserva import ReservaResposta
from app.services.reserva import ReservaService

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.get("/{id_reserva}", response_model=ReservaResposta)
def buscar_por_id(
    id_reserva: int,
    usuario: UsuarioAtual = Depends(obter_usuario_atual),
    service: ReservaService = Depends(),
) -> ReservaResposta:
    return service.buscar_por_id(id_reserva, usuario)
