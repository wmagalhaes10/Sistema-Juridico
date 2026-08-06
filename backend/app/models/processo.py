import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import FaseProcessual, StatusProcesso
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Processo(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "processos"

    numero_cnj: Mapped[str] = mapped_column(String(25), nullable=False, unique=True, index=True)
    vara: Mapped[str | None] = mapped_column(String(255))
    tribunal: Mapped[str | None] = mapped_column(String(50))
    comarca: Mapped[str | None] = mapped_column(String(255))
    tipo_acao: Mapped[str | None] = mapped_column(String(255))
    fase_processual: Mapped[FaseProcessual] = mapped_column(
        Enum(FaseProcessual, name="fase_processual"), nullable=False, default=FaseProcessual.CONHECIMENTO
    )
    polo_ativo: Mapped[str | None] = mapped_column(String(500))
    polo_passivo: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[StatusProcesso] = mapped_column(
        Enum(StatusProcesso, name="status_processo"), nullable=False, default=StatusProcesso.ATIVO
    )
    data_distribuicao: Mapped[date | None] = mapped_column(Date)
    valor_causa: Mapped[float | None] = mapped_column(Numeric(14, 2))
    ultima_consulta_datajud: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    cliente_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("clientes.id"), nullable=False)
    advogado_responsavel_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))

    cliente: Mapped["Cliente"] = relationship(back_populates="processos")  # noqa: F821
    advogado_responsavel: Mapped["User"] = relationship(back_populates="processos")  # noqa: F821
    movimentacoes: Mapped[list["Movimentacao"]] = relationship(  # noqa: F821
        back_populates="processo", cascade="all, delete-orphan", order_by="desc(Movimentacao.data_movimentacao)"
    )
    prazos: Mapped[list["Prazo"]] = relationship(  # noqa: F821
        back_populates="processo", cascade="all, delete-orphan"
    )
    contratos_honorarios: Mapped[list["ContratoHonorario"]] = relationship(back_populates="processo")  # noqa: F821
    despesas: Mapped[list["Despesa"]] = relationship(  # noqa: F821
        back_populates="processo", cascade="all, delete-orphan"
    )
