from fastapi import APIRouter, Depends, Query

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


@router.get("", response_model=list[ReservaResposta])
def listar(
    limite: int = Query(20, ge=1, le=100),
    deslocamento: int = Query(0, ge=0),
    usuario: UsuarioAtual = Depends(obter_usuario_atual),
    service: ReservaService = Depends(),
) -> list[ReservaResposta]:
    return service.listar(usuario, limite, deslocamento)


@router.post("/{id_reserva}/cancelar", response_model=ReservaResposta)
def cancelar(
    id_reserva: int,
    usuario: UsuarioAtual = Depends(obter_usuario_atual),
    service: ReservaService = Depends(),
) -> ReservaResposta:
    return service.cancelar(id_reserva, usuario)
