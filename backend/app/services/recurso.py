from collections.abc import Sequence

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import obter_sessao
from app.models import Recurso
from app.repositories.recurso import RecursoRepository
from app.schemas.recurso import RecursoAtualizar, RecursoCriar
from app.services.excecoes import RecursoEmUso, RecursoNaoEncontrado


class RecursoService:
    def __init__(self, sessao: Session = Depends(obter_sessao)) -> None:
        self._repo = RecursoRepository(sessao)

    def buscar_por_id(self, id_recurso: int) -> Recurso:
        recurso = self._repo.buscar_por_id(id_recurso)
        if recurso is None:
            raise RecursoNaoEncontrado
        return recurso

    def criar(self, dados: RecursoCriar) -> Recurso:
        recurso = Recurso(**dados.model_dump(), status_recurso="ativo")
        return self._repo.criar(recurso)

    def listar(self, limite: int, deslocamento: int) -> Sequence[Recurso]:
        return self._repo.listar(limite, deslocamento)

    def atualizar(self, id_recurso: int, dados: RecursoAtualizar) -> Recurso:
        recurso = self.buscar_por_id(id_recurso)
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(recurso, campo, valor)
        return self._repo.atualizar(recurso)

    def remover(self, id_recurso: int) -> None:
        recurso = self.buscar_por_id(id_recurso)
        try:
            self._repo.remover(recurso)
        except IntegrityError as erro:
            raise RecursoEmUso from erro
