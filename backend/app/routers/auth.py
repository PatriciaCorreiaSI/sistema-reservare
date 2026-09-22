from fastapi import APIRouter, Depends

from app.schemas.auth import LoginEntrada, RefreshEntrada, TokenResposta
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResposta)
def login(dados: LoginEntrada, service: AuthService = Depends()) -> TokenResposta:
    return service.login(dados)


@router.post("/refresh", response_model=TokenResposta)
def renovar(dados: RefreshEntrada, service: AuthService = Depends()) -> TokenResposta:
    return service.renovar(dados)


# 204 revogado com sucesso e não retorna dados
@router.post("/logout", status_code=204)
def logout(dados: RefreshEntrada, service: AuthService = Depends()) -> None:
    service.logout(dados)
