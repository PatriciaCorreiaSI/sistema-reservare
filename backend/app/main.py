from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers import auth, health, recurso, usuario
from app.services.excecoes import (
    CredenciaisInvalidas,
    EmailJaCadastrado,
    PrivilegioInsuficiente,
    RecursoEmUso,
    RecursoNaoEncontrado,
)

app = FastAPI()
app.include_router(health.router)
app.include_router(recurso.router)
app.include_router(auth.router)
app.include_router(usuario.router)


@app.exception_handler(RecursoNaoEncontrado)
def traduzir_nao_encontrado(
    request: Request, exc: RecursoNaoEncontrado
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": "Recurso não encontrado"},
    )


@app.exception_handler(RecursoEmUso)
def traduzir_em_uso(request: Request, exc: RecursoEmUso) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": "Recurso possui reservas e não pode ser removido"},
    )


# A RFC 7235 exige WWW-Authenticate em todo 401; o 403 não leva,
# porque ali o servidor já sabe quem chama e não há autenticação a negociar.
@app.exception_handler(CredenciaisInvalidas)
def traduzir_credenciais_invalidas(
    request: Request, exc: CredenciaisInvalidas
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": "Login, refresh ou access inválidos"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(PrivilegioInsuficiente)
def traduzir_privilegio_insuficiente(
    request: Request, exc: PrivilegioInsuficiente
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"detail": "Privilégio insuficiente"},
    )


@app.exception_handler(EmailJaCadastrado)
def traduzir_email_ja_cadastrado(
    request: Request, exc: EmailJaCadastrado
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": "E-mail já cadastrado"},
    )
