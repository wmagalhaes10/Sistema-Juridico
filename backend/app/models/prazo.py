import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import StatusPrazo, TipoPrazo
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Prazo(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "prazos"

    processo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("processos.id"), nullable=False)
    responsavel_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))
    movimentacao_origem_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("movimentacoes.id"))

    data_prazo: Mapped[date] = mapped_column(Date, nullable=False)
    tipo: Mapped[TipoPrazo] = mapped_column(Enum(TipoPrazo, name="tipo_prazo"), nullable=False)
    status: Mapped[StatusPrazo] = mapped_column(
        Enum(StatusPrazo, name="status_prazo"), nullable=False, default=StatusPrazo.PENDENTE
    )
    descricao: Mapped[str | None] = mapped_column(Text)

    processo: Mapped["Processo"] = relationship(back_populates="prazos")  # noqa: F821
    responsavel: Mapped["User"] = relationship(back_populates="prazos")  # noqa: F821
    movimentacao_origem: Mapped["Movimentacao"] = relationship(back_populates="prazos_gerados")  # noqa: F821
