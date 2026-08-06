from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class User(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "users"

    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    oab: Mapped[str | None] = mapped_column(String(20))
    super_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    processos: Mapped[list["Processo"]] = relationship(back_populates="advogado_responsavel")  # noqa: F821
    prazos: Mapped[list["Prazo"]] = relationship(back_populates="responsavel")  # noqa: F821
    permissoes: Mapped[list["Permissao"]] = relationship(  # noqa: F821
        back_populates="usuario", cascade="all, delete-orphan"
    )
