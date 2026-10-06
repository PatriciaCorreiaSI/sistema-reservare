from fastapi import APIRouter, Cookie, Depends, Response

from app.schemas.auth import LoginEntrada, TokenResposta
from app.security import REFRESH_DIAS
from app.services.auth import AuthService, ParDeTokens

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# ADR 0023: o refresh viaja num cookie, nunca no corpo. Nome e caminho num lugar
# só, porque o logout só apaga o cookie se o path for idêntico ao que o gravou.
# O caminho é o prefixo do main.py ("/api") somado ao deste router ("/auth").
COOKIE_REFRESH = "refresh_token"
CAMINHO_DO_COOKIE = "/api/auth"


def _responder(response: Response, tokens: ParDeTokens) -> TokenResposta:
    # O refresh vai no cabeçalho Set-cookie; só o access vai no corpo.
    response.set_cookie(
        key=COOKIE_REFRESH,
        value=tokens.refresh,
        max_age=REFRESH_DIAS * 24 * 60 * 60,
        path=CAMINHO_DO_COOKIE,
        secure=True,
        httponly=True,
        samesite="strict",
    )
    return TokenResposta(access_token=tokens.access)


@router.post("/login", response_model=TokenResposta)
def login(
    dados: LoginEntrada, response: Response, service: AuthService = Depends()
) -> TokenResposta:
    return _responder(response, service.login(dados))


@router.post("/refresh", response_model=TokenResposta)
def renovar(
    response: Response,
    service: AuthService = Depends(),
    refresh_token: str | None = Cookie(default=None, alias=COOKIE_REFRESH),
) -> TokenResposta:
    return _responder(response, service.renovar(refresh_token))


# 204 revogado com sucesso e sem o corpo. Apagar o cookie é Set-Cookie cm Max-Age=0,
# e só funciona com o mesmo nome e o mesmo path do que gravou.
@router.post("/logout", status_code=204)
def logout(
    response: Response,
    service: AuthService = Depends(),
    refresh_token: str | None = Cookie(default=None, alias=COOKIE_REFRESH),
) -> None:
    service.logout(refresh_token)
    response.delete_cookie(
        key=COOKIE_REFRESH,
        path=CAMINHO_DO_COOKIE,
        secure=True,
        httponly=True,
        samesite="strict",
    )
