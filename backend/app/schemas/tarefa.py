import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import StatusTarefa


class TarefaCreate(BaseModel):
    titulo: str
    descricao: str | None = None
    data_vencimento: date | None = None
    responsavel_id: uuid.UUID | None = None
    processo_id: uuid.UUID | None = None


class TarefaUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    data_vencimento: date | None = None
    responsavel_id: uuid.UUID | None = None
    status: StatusTarefa | None = None


class UsuarioResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str


class ProcessoResumoTarefa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    numero_cnj: str


class TarefaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    titulo: str
    descricao: str | None
    data_vencimento: date | None
    status: StatusTarefa
    processo_id: uuid.UUID | None
    responsavel_id: uuid.UUID | None
    criado_por_id: uuid.UUID
    responsavel: UsuarioResumo | None = None
    processo: ProcessoResumoTarefa | None = None
