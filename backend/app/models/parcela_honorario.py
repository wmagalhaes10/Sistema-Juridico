import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Numeric, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import StatusParcela
from app.models.mixins import TimestampMixin, UUIDPKMixin


class ParcelaHonorario(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "parcelas_honorarios"

    contrato_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("contratos_honorarios.id"), nullable=False)

    numero_parcela: Mapped[int] = mapped_column(nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    data_pagamento: Mapped[date | None] = mapped_column(Date)
    status: Mapped[StatusParcela] = mapped_column(
        Enum(StatusParcela, name="status_parcela"), nullable=False, default=StatusParcela.PENDENTE
    )

    contrato: Mapped["ContratoHonorario"] = relationship(back_populates="parcelas")  # noqa: F821
