import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatusPublicacao


class ProcessoResumoPublicacao(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    numero_cnj: str


class PublicacaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    id_djen: int
    data_disponibilizacao: date
    sigla_tribunal: str | None
    tipo_comunicacao: str | None
    tipo_documento: str | None
    nome_orgao: str | None
    nome_classe: str | None
    numero_processo: str | None
    texto: str | None
    link: str | None
    meio: str | None
    oab_numero: str | None
    oab_uf: str | None
    status: StatusPublicacao
    processo_id: uuid.UUID | None
    processo: ProcessoResumoPublicacao | None = None


class PublicacaoListResponse(BaseModel):
    items: list[PublicacaoRead]
    total: int
    page: int
    page_size: int


class PublicacaoStatusUpdate(BaseModel):
    status: StatusPublicacao


class PublicacoesResumo(BaseModel):
    nao_tratadas: int
    tratadas: int
    descartadas: int
    nao_tratadas_hoje: int
