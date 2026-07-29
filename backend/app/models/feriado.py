from datetime import date

from sqlalchemy import Date, Enum, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import TipoFeriado
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Feriado(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "feriados"
    __table_args__ = (UniqueConstraint("data", "uf", name="uq_feriado_data_uf"),)

    data: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[TipoFeriado] = mapped_column(Enum(TipoFeriado, name="tipo_feriado"), nullable=False)
    uf: Mapped[str | None] = mapped_column(String(2))
