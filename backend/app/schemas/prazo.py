import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatusPrazo, TipoPrazo


class PrazoBase(BaseModel):
    data_prazo: date
    tipo: TipoPrazo
    descricao: str | None = None
    responsavel_id: uuid.UUID | None = None


class PrazoCreate(PrazoBase):
    pass


class PrazoUpdate(BaseModel):
    data_prazo: date | None = None
    tipo: TipoPrazo | None = None
    status: StatusPrazo | None = None
    descricao: str | None = None
    responsavel_id: uuid.UUID | None = None


class ProcessoResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    numero_cnj: str


class PrazoRead(PrazoBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    processo_id: uuid.UUID
    status: StatusPrazo
    movimentacao_origem_id: uuid.UUID | None
    processo: ProcessoResumo | None = None


class PrazoListResponse(BaseModel):
    items: list[PrazoRead]
    total: int
    page: int
    page_size: int


class DashboardPrazos(BaseModel):
    inicio: date
    fim: date
    total_pendentes: int
    vencidos: int
    prazos: list[PrazoRead]
