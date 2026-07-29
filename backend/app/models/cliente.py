from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import TipoPessoa
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Cliente(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "clientes"

    tipo_pessoa: Mapped[TipoPessoa] = mapped_column(Enum(TipoPessoa, name="tipo_pessoa"), nullable=False)
    cpf_cnpj: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    nome_razao_social: Mapped[str] = mapped_column(String(255), nullable=False)
    endereco: Mapped[str | None] = mapped_column(String(500))
    telefone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(255))
    oab_responsavel: Mapped[str | None] = mapped_column(String(20))

    processos: Mapped[list["Processo"]] = relationship(back_populates="cliente")  # noqa: F821
    contratos_honorarios: Mapped[list["ContratoHonorario"]] = relationship(back_populates="cliente")  # noqa: F821
