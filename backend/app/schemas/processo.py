import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.validators import numero_cnj_valido, somente_digitos
from app.models.enums import FaseProcessual, OrigemMovimentacao, StatusProcesso


class ProcessoBase(BaseModel):
    numero_cnj: str
    vara: str | None = None
    tribunal: str | None = None
    comarca: str | None = None
    tipo_acao: str | None = None
    fase_processual: FaseProcessual = FaseProcessual.CONHECIMENTO
    polo_ativo: str | None = None
    polo_passivo: str | None = None
    status: StatusProcesso = StatusProcesso.ATIVO
    data_distribuicao: date | None = None
    valor_causa: Decimal | None = None

    @field_validator("numero_cnj")
    @classmethod
    def valida_numero_cnj(cls, v: str) -> str:
        if not numero_cnj_valido(v):
            raise ValueError("Número CNJ inválido")
        return somente_digitos(v)


class ProcessoCreate(ProcessoBase):
    cliente_id: uuid.UUID
    advogado_responsavel_id: uuid.UUID | None = None


class ProcessoUpdate(BaseModel):
    vara: str | None = None
    tribunal: str | None = None
    comarca: str | None = None
    tipo_acao: str | None = None
    fase_processual: FaseProcessual | None = None
    polo_ativo: str | None = None
    polo_passivo: str | None = None
    status: StatusProcesso | None = None
    data_distribuicao: date | None = None
    valor_causa: Decimal | None = None
    advogado_responsavel_id: uuid.UUID | None = None


class ClienteResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome_razao_social: str


class ProcessoRead(ProcessoBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cliente_id: uuid.UUID
    advogado_responsavel_id: uuid.UUID | None
    ultima_consulta_datajud: datetime | None
    cliente: ClienteResumo | None = None


class ProcessoListResponse(BaseModel):
    items: list[ProcessoRead]
    total: int
    page: int
    page_size: int


class MovimentacaoCreate(BaseModel):
    data_movimentacao: datetime
    descricao: str


class MovimentacaoRead(MovimentacaoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    processo_id: uuid.UUID
    origem: OrigemMovimentacao
