import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import TipoFeriado


class FeriadoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    data: date
    nome: str
    tipo: TipoFeriado
    uf: str | None
