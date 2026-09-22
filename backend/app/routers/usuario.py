from fastapi import APIRouter, Depends

from app.dependencies import exigir_admin
from app.schemas.usuario import UsuarioCriar, UsuarioResposta
from app.services.usuario import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


# 201 = criado com sucesso; exigir_admin devolve 401 sem token e 403 sem privilégio
@router.post(
    "",
    status_code=201,
    response_model=UsuarioResposta,
    dependencies=[Depends(exigir_admin)],
)
def criar(dados: UsuarioCriar, service: UsuarioService = Depends()) -> UsuarioResposta:
    return UsuarioResposta.model_validate(service.criar(dados))
