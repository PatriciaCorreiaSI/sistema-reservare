from fastapi import APIRouter, Depends

from app.schemas.recurso import RecursoResposta
from app.services.recurso import RecursoService

router = APIRouter(prefix="/recursos", tags=["Recursos"])


@router.get("/{id_recurso}", response_model=RecursoResposta)
def buscar_por_id(
    id_recurso: int, service: RecursoService = Depends()
) -> RecursoResposta:
    return RecursoResposta.model_validate(service.buscar_por_id(id_recurso))
