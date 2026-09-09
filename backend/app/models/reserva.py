from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Identity, String
from sqlalchemy.dialects.postgresql import TSTZRANGE, ExcludeConstraint, Range
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Reserva(Base):
    __tablename__ = "reserva"

    id_reserva: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="RESTRICT"), index=True
    )
    id_recurso: Mapped[int] = mapped_column(
        ForeignKey("recurso.id_recurso", ondelete="RESTRICT"), index=True
    )
    convidados: Mapped[int] = mapped_column()
    periodo: Mapped[Range[datetime]] = mapped_column(
        TSTZRANGE(), comment="Ocupa um trecho de tempo com início e fim"
    )
    status_reserva: Mapped[str] = mapped_column(String(30))
    cancelada_por_id_usuario: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="RESTRICT"), index=True
    )
    cancelada_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), comment="Tipo de instante com fuso"
    )

    __table_args__ = (
        ExcludeConstraint(
            (id_recurso, "="),
            (periodo, "&&"),
            name="ex_reserva_sem_sobreposicao",
            where=(cancelada_em.is_(None)),
        ),
        CheckConstraint(
            """
            NOT isempty(periodo) 
            AND lower_inc(periodo) 
            AND NOT upper_inc(periodo) 
            AND NOT upper_inf(periodo) 
            AND NOT lower_inf(periodo)
            """,
            name="formato_semiaberto",
        ),
        CheckConstraint("convidados > 0", name="convidados_positivos"),
        CheckConstraint("status_reserva IN ('confirmada', 'cancelada')", name="status"),
        CheckConstraint(
            """
            (
                status_reserva = 'cancelada' 
                AND cancelada_em IS NOT NULL 
                AND cancelada_por_id_usuario IS NOT NULL
            ) 
            OR (
                status_reserva = 'confirmada' 
                AND cancelada_em IS NULL 
                AND cancelada_por_id_usuario IS NULL
            )
            """,
            name="cancelamento",
        ),
    )
