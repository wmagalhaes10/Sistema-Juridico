import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.enums import StatusParcela


class ParcelaUpdate(BaseModel):
    data_vencimento: date | None = None
    data_pagamento: date | None = None


class ParcelaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    contrato_id: uuid.UUID
    numero_parcela: int
    valor: Decimal
    data_vencimento: date
    data_pagamento: date | None
    status: StatusParcela

    @model_validator(mode="after")
    def calcula_status_efetivo(self) -> "ParcelaRead":
        """Deriva o status em tempo real: uma parcela pendente que passou do
        vencimento aparece como atrasada mesmo antes da rotina diária (Celery)
        sincronizar o campo persistido."""
        if self.data_pagamento is not None:
            self.status = StatusParcela.PAGO
        elif self.data_vencimento < date.today():
            self.status = StatusParcela.ATRASADO
        else:
            self.status = StatusParcela.PENDENTE
        return self
