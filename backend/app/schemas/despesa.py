import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enums import TipoDespesa


class DespesaCreate(BaseModel):
    tipo: TipoDespesa
    descricao: str | None = None
    valor: Decimal
    data_despesa: date

    @field_validator("valor")
    @classmethod
    def valida_valor(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("valor deve ser maior que zero")
        return v


class DespesaRead(DespesaCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    processo_id: uuid.UUID
