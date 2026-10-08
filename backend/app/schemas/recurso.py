from datetime import date, datetime, time
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator


class RecursoCriar(BaseModel):
    nome_recurso: str
    ocupacao: int = Field(gt=0)
    hora_func_inicio: time
    hora_func_fim: time

    @model_validator(mode="after")
    def validar_periodo(self) -> Self:
        if self.hora_func_inicio >= self.hora_func_fim:
            raise ValueError(
                "Período de funcionamento inválido: "
                "hora_func_inicio precisa ser anterior a hora_func_fim."
            )
        return self


class RecursoAtualizar(BaseModel):
    nome_recurso: str | None = None
    ocupacao: int | None = Field(default=None, gt=0)
    hora_func_inicio: time | None = None
    hora_func_fim: time | None = None
    status_recurso: Literal["ativo", "inativo"] | None = None


class RecursoResposta(BaseModel):
    id_recurso: int
    nome_recurso: str
    ocupacao: int
    hora_func_inicio: time
    hora_func_fim: time
    status_recurso: str
    fuso: str


class Lacuna(BaseModel):
    inicio: datetime
    fim: datetime


class DisponibilidadeResposta(BaseModel):
    id_recurso: int
    dia: date
    lacunas: list[Lacuna]
