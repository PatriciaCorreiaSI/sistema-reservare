from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers import health, recurso
from app.services.excecoes import RecursoEmUso, RecursoNaoEncontrado

app = FastAPI()
app.include_router(health.router)
app.include_router(recurso.router)


@app.exception_handler(RecursoNaoEncontrado)
def traduzir_nao_encontrado(
    request: Request, exc: RecursoNaoEncontrado
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "Recurso não encontrado"})


@app.exception_handler(RecursoEmUso)
def traduzir_em_uso(request: Request, exc: RecursoEmUso) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": "Recurso possui reservas e não pode ser removido"},
    )
