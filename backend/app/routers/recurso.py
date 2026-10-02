from datetime import date

from fastapi import APIRouter, Depends, Query

from app.dependencies import exigir_admin, obter_usuario_atual
from app.schemas.recurso import (
    DisponibilidadeResposta,
    RecursoAtualizar,
    RecursoCriar,
    RecursoResposta,
)
from app.services.recurso import RecursoService
from app.services.reserva import ReservaService

router = APIRouter(prefix="/recursos", tags=["Recursos"])


@router.get(
    "/{id_recurso}",
    response_model=RecursoResposta,
    dependencies=[Depends(obter_usuario_atual)],
)
def buscar_por_id(
    id_recurso: int, service: RecursoService = Depends()
) -> RecursoResposta:
    return RecursoResposta.model_validate(service.buscar_por_id(id_recurso))


# 201 = criado com sucesso
@router.post(
    "",
    status_code=201,
    response_model=RecursoResposta,
    dependencies=[Depends(exigir_admin)],
)
def criar(dados: RecursoCriar, service: RecursoService = Depends()) -> RecursoResposta:
    return RecursoResposta.model_validate(service.criar(dados))


@router.get(
    "",
    response_model=list[RecursoResposta],
    dependencies=[Depends(obter_usuario_atual)],
)
def listar(
    limite: int = Query(20, ge=1, le=100),
    deslocamento: int = Query(0, ge=0),
    service: RecursoService = Depends(),
) -> list[RecursoResposta]:
    return [
        RecursoResposta.model_validate(r) for r in service.listar(limite, deslocamento)
    ]


@router.patch(
    "/{id_recurso}",
    response_model=RecursoResposta,
    dependencies=[Depends(exigir_admin)],
)
def atualizar(
    id_recurso: int, dados: RecursoAtualizar, service: RecursoService = Depends()
) -> RecursoResposta:
    return RecursoResposta.model_validate(service.atualizar(id_recurso, dados))


# 204 = removido com sucesso e não retorna dados
@router.delete(
    "/{id_recurso}",
    status_code=204,
    dependencies=[Depends(exigir_admin)],
)
def remover(id_recurso: int, service: RecursoService = Depends()) -> None:
    service.remover(id_recurso)


@router.get(
    "/{id_recurso}/disponibilidade",
    response_model=DisponibilidadeResposta,
    dependencies=[Depends(obter_usuario_atual)],
)
def disponibilidade(
    id_recurso: int, dia: date, service: ReservaService = Depends()
) -> DisponibilidadeResposta:
    return service.disponibilidade(id_recurso, dia)
