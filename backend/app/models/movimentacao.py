import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import OrigemMovimentacao
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Movimentacao(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "movimentacoes"

    processo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("processos.id"), nullable=False)
    data_movimentacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    origem: Mapped[OrigemMovimentacao] = mapped_column(
        Enum(OrigemMovimentacao, name="origem_movimentacao"), nullable=False, default=OrigemMovimentacao.MANUAL
    )

    processo: Mapped["Processo"] = relationship(back_populates="movimentacoes")  # noqa: F821
    prazos_gerados: Mapped[list["Prazo"]] = relationship(back_populates="movimentacao_origem")  # noqa: F821
