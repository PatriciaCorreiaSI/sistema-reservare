from datetime import date
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query

from app.dependencies import exigir_admin, obter_fuso, obter_usuario_atual
from app.models import Recurso
from app.schemas.recurso import (
    DisponibilidadeResposta,
    RecursoAtualizar,
    RecursoCriar,
    RecursoResposta,
)
from app.services.recurso import RecursoService
from app.services.reserva import ReservaService

router = APIRouter(prefix="/recursos", tags=["Recursos"])


def _resposta(recurso: Recurso, fuso: ZoneInfo) -> RecursoResposta:
    # Emenda ao ADR 0018: o fuso vai junto, porque hora_func em fuso é meia
    # informação. Composto aqui porque o schema não lê e o modelo não
    # tem a coluna; o valor vem da mesma dependência que o ReservaService usa.
    return RecursoResposta(
        id_recurso=recurso.id_recurso,
        nome_recurso=recurso.nome_recurso,
        ocupacao=recurso.ocupacao,
        hora_func_inicio=recurso.hora_func_inicio,
        hora_func_fim=recurso.hora_func_fim,
        status_recurso=recurso.status_recurso,
        fuso=fuso.key,
    )


@router.get(
    "/{id_recurso}",
    response_model=RecursoResposta,
    dependencies=[Depends(obter_usuario_atual)],
)
def buscar_por_id(
    id_recurso: int,
    service: RecursoService = Depends(),
    fuso: ZoneInfo = Depends(obter_fuso),
) -> RecursoResposta:
    return _resposta(service.buscar_por_id(id_recurso), fuso)


# 201 = criado com sucesso
@router.post(
    "",
    status_code=201,
    response_model=RecursoResposta,
    dependencies=[Depends(exigir_admin)],
)
def criar(
    dados: RecursoCriar,
    service: RecursoService = Depends(),
    fuso: ZoneInfo = Depends(obter_fuso),
) -> RecursoResposta:
    return _resposta(service.criar(dados), fuso)


@router.get(
    "",
    response_model=list[RecursoResposta],
    dependencies=[Depends(obter_usuario_atual)],
)
def listar(
    limite: int = Query(20, ge=1, le=100),
    deslocamento: int = Query(0, ge=0),
    service: RecursoService = Depends(),
    fuso: ZoneInfo = Depends(obter_fuso),
) -> list[RecursoResposta]:
    return [_resposta(r, fuso) for r in service.listar(limite, deslocamento)]


@router.patch(
    "/{id_recurso}",
    response_model=RecursoResposta,
    dependencies=[Depends(exigir_admin)],
)
def atualizar(
    id_recurso: int,
    dados: RecursoAtualizar,
    service: RecursoService = Depends(),
    fuso: ZoneInfo = Depends(obter_fuso),
) -> RecursoResposta:
    return _resposta(service.atualizar(id_recurso, dados), fuso)


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
