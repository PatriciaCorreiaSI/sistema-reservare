from fastapi import APIRouter, Depends

from app.dependencies import UsuarioAtual, obter_usuario_atual
from app.schemas.reserva import ReservaCriar, ReservaResposta
from app.services.reserva import ReservaService

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.get("/{id_reserva}", response_model=ReservaResposta)
def buscar_por_id(
    id_reserva: int,
    usuario: UsuarioAtual = Depends(obter_usuario_atual),
    service: ReservaService = Depends(),
) -> ReservaResposta:
    return service.buscar_por_id(id_reserva, usuario)


@router.post("", status_code=201, response_model=ReservaResposta)
def criar(
    dados: ReservaCriar,
    usuario: UsuarioAtual = Depends(obter_usuario_atual),
    service: ReservaService = Depends(),
) -> ReservaResposta:
    return service.criar(dados, usuario)
