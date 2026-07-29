import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import TipoDespesa
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Despesa(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "despesas"

    processo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("processos.id"), nullable=False)

    tipo: Mapped[TipoDespesa] = mapped_column(Enum(TipoDespesa, name="tipo_despesa"), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(500))
    valor: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    data_despesa: Mapped[date] = mapped_column(Date, nullable=False)

    processo: Mapped["Processo"] = relationship(back_populates="despesas")  # noqa: F821
