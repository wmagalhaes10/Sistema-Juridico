import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import TipoContrato
from app.models.mixins import TimestampMixin, UUIDPKMixin


class ContratoHonorario(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "contratos_honorarios"

    cliente_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("clientes.id"), nullable=False)
    processo_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("processos.id"))

    tipo: Mapped[TipoContrato] = mapped_column(Enum(TipoContrato, name="tipo_contrato"), nullable=False)
    valor_contratado: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    numero_parcelas: Mapped[int] = mapped_column(nullable=False, default=1)
    data_assinatura: Mapped[date | None] = mapped_column(Date)
    observacoes: Mapped[str | None] = mapped_column(Text)

    cliente: Mapped["Cliente"] = relationship(back_populates="contratos_honorarios")  # noqa: F821
    processo: Mapped["Processo"] = relationship(back_populates="contratos_honorarios")  # noqa: F821
    parcelas: Mapped[list["ParcelaHonorario"]] = relationship(  # noqa: F821
        back_populates="contrato", cascade="all, delete-orphan", order_by="ParcelaHonorario.numero_parcela"
    )
