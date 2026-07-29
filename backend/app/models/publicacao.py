import uuid
from datetime import date

from sqlalchemy import BigInteger, Date, Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import StatusPublicacao
from app.models.mixins import TimestampMixin, UUIDPKMixin


class Publicacao(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "publicacoes"

    # id da comunicação no DJEN — chave de idempotência da sincronização
    id_djen: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True, index=True)

    data_disponibilizacao: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    sigla_tribunal: Mapped[str | None] = mapped_column(String(20))
    tipo_comunicacao: Mapped[str | None] = mapped_column(String(100))
    tipo_documento: Mapped[str | None] = mapped_column(String(100))
    nome_orgao: Mapped[str | None] = mapped_column(String(255))
    nome_classe: Mapped[str | None] = mapped_column(String(255))
    numero_processo: Mapped[str | None] = mapped_column(String(25), index=True)
    texto: Mapped[str | None] = mapped_column(Text)
    link: Mapped[str | None] = mapped_column(String(500))
    meio: Mapped[str | None] = mapped_column(String(100))
    oab_numero: Mapped[str | None] = mapped_column(String(20))
    oab_uf: Mapped[str | None] = mapped_column(String(2))

    status: Mapped[StatusPublicacao] = mapped_column(
        Enum(StatusPublicacao, name="status_publicacao"), nullable=False, default=StatusPublicacao.NAO_TRATADA
    )

    processo_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("processos.id"))
    tratada_por_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id"))

    processo: Mapped["Processo"] = relationship(foreign_keys=[processo_id])  # noqa: F821
    tratada_por: Mapped["User"] = relationship(foreign_keys=[tratada_por_id])  # noqa: F821
