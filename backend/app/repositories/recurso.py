from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Recurso


class RecursoRepository:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def buscar_por_id(self, id_recurso: int) -> Recurso | None:
        consulta = select(Recurso).where(Recurso.id_recurso == id_recurso)
        return self._sessao.scalar(consulta)

    def buscar_por_nome(self, nome_recurso: str) -> Recurso | None:
        """O de menor id_recurso com esse nome, ou None. Sem UNIQUE no nome:
        o order_by é o desempate decidido no desenho da semeadura."""
        consulta = (
            select(Recurso)
            .where(Recurso.nome_recurso == nome_recurso)
            .order_by(Recurso.id_recurso)
        )
        return self._sessao.scalar(consulta)

    def listar(self, limite: int, deslocamento: int) -> Sequence[Recurso]:
        consulta = (
            select(Recurso)
            .order_by(Recurso.id_recurso)
            .limit(limite)
            .offset(deslocamento)
        )
        return self._sessao.scalars(consulta).all()

    def criar(self, recurso: Recurso) -> Recurso:
        self._sessao.add(recurso)
        self._sessao.flush()
        return recurso

    def atualizar(self, recurso: Recurso) -> Recurso:
        self._sessao.flush()
        return recurso

    def remover(self, recurso: Recurso) -> None:
        self._sessao.delete(recurso)
        self._sessao.flush()
