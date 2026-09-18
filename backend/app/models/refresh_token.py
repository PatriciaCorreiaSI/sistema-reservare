import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Identity, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id_refresh_token: Mapped[int] = mapped_column(
        Identity(always=True), primary_key=True
    )
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"), index=True
    )
    hash_token: Mapped[str] = mapped_column(
        String(64), comment="Hash de 64 caracteres gerado por SHA-256", unique=True
    )
    familia_token: Mapped[uuid.UUID] = mapped_column(
        UUID(), comment="De qual login este descende", index=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        comment="instante em que o token foi emitido (no login ou na rotação)",
    )
    expira_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), comment="Depois disso o token não vale, mesmo revogado"
    )
    revogado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        comment="NULL permitido, e o nulo é o estado normal (vivo). "
        "Preenchido no logout, na rotação e na detecção de reuso",
    )

    __table_args__ = (
        CheckConstraint("expira_em > criado_em", name="expira_depois_de_criado"),
    )
