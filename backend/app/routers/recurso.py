from fastapi import APIRouter, Depends

from app.schemas.recurso import RecursoAtualizar, RecursoCriar, RecursoResposta
from app.services.recurso import RecursoService

router = APIRouter(prefix="/recursos", tags=["Recursos"])


@router.get("/{id_recurso}", response_model=RecursoResposta)
def buscar_por_id(
    id_recurso: int, service: RecursoService = Depends()
) -> RecursoResposta:
    return RecursoResposta.model_validate(service.buscar_por_id(id_recurso))


# 201 = criado com sucesso
@router.post("", status_code=201, response_model=RecursoResposta)
def criar(dados: RecursoCriar, service: RecursoService = Depends()) -> RecursoResposta:
    return RecursoResposta.model_validate(service.criar(dados))


@router.get("", response_model=list[RecursoResposta])
def listar(
    limite: int = 20, deslocamento: int = 0, service: RecursoService = Depends()
) -> list[RecursoResposta]:
    return [
        RecursoResposta.model_validate(r) for r in service.listar(limite, deslocamento)
    ]


@router.patch("/{id_recurso}", response_model=RecursoResposta)
def atualizar(
    id_recurso: int, dados: RecursoAtualizar, service: RecursoService = Depends()
) -> RecursoResposta:
    return RecursoResposta.model_validate(service.atualizar(id_recurso, dados))


# 204 = removido com sucesso e não retorna dados
@router.delete("/{id_recurso}", status_code=204)
def remover(id_recurso: int, service: RecursoService = Depends()) -> None:
    service.remover(id_recurso)
