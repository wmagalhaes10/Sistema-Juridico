import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import StatusTarefa
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Tarefa(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "tarefas"

    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    data_vencimento: Mapped[date | None] = mapped_column(Date)
    status: Mapped[StatusTarefa] = mapped_column(
        Enum(StatusTarefa, name="status_tarefa"), nullable=False, default=StatusTarefa.PENDENTE
    )

    processo_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("processos.id"))
    responsavel_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))
    criado_por_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)

    processo: Mapped["Processo"] = relationship(foreign_keys=[processo_id])  # noqa: F821
    responsavel: Mapped["User"] = relationship(foreign_keys=[responsavel_id])  # noqa: F821
    criado_por: Mapped["User"] = relationship(foreign_keys=[criado_por_id])  # noqa: F821
