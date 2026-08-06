import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.models.enums import TipoContrato
from app.schemas.parcela import ParcelaRead


class ContratoHonorarioCreate(BaseModel):
    cliente_id: uuid.UUID
    processo_id: uuid.UUID | None = None
    tipo: TipoContrato
    valor_contratado: Decimal
    numero_parcelas: int = 1
    data_assinatura: date | None = None
    observacoes: str | None = None

    @field_validator("valor_contratado")
    @classmethod
    def valida_valor(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("valor_contratado deve ser maior que zero")
        return v

    @model_validator(mode="after")
    def valida_parcelas(self) -> "ContratoHonorarioCreate":
        if self.numero_parcelas < 1:
            raise ValueError("numero_parcelas deve ser maior ou igual a 1")
        return self


class ContratoHonorarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cliente_id: uuid.UUID
    processo_id: uuid.UUID | None
    tipo: TipoContrato
    valor_contratado: Decimal
    numero_parcelas: int
    data_assinatura: date | None
    observacoes: str | None
    parcelas: list[ParcelaRead] = []
