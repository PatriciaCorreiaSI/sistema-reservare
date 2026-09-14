from datetime import time

from pydantic import BaseModel, ConfigDict


class RecursoCriar(BaseModel):
    nome_recurso: str
    ocupacao: int
    hora_func_inicio: time
    hora_func_fim: time


class RecursoAtualizar(BaseModel):
    nome_recurso: str | None = None
    ocupacao: int | None = None
    hora_func_inicio: time | None = None
    hora_func_fim: time | None = None
    status_recurso: str | None = None


class RecursoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_recurso: int
    nome_recurso: str
    ocupacao: int
    hora_func_inicio: time
    hora_func_fim: time
    status_recurso: str
