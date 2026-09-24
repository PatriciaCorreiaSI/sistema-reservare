from datetime import datetime
from typing import Self

from pydantic import AwareDatetime, BaseModel, Field, model_validator


class ReservaCriar(BaseModel):
    id_recurso: int
    convidados: int = Field(gt=0)
    inicio: AwareDatetime
    fim: AwareDatetime

    @model_validator(mode="after")
    def validar_periodo(self) -> Self:
        raise NotImplementedError


class ReservaResposta(BaseModel):
    id_reserva: int
    id_usuario: int
    id_recurso: int
    convidados: int
    inicio: datetime
    fim: datetime
    status_reserva: str
    cancelada_por_id_usuario: int | None
    cancelada_em: datetime | None
