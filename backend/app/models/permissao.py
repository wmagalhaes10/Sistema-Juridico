import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ModuloSistema
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Permissao(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "permissoes"
    __table_args__ = (UniqueConstraint("user_id", "modulo", name="uq_permissao_user_modulo"),)

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    modulo: Mapped[ModuloSistema] = mapped_column(Enum(ModuloSistema, name="modulo_sistema"), nullable=False)

    pode_visualizar: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    pode_editar: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    pode_excluir: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    usuario: Mapped["User"] = relationship(back_populates="permissoes")  # noqa: F821
