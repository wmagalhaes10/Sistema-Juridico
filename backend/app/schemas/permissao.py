import uuid

from pydantic import BaseModel, ConfigDict

from app.models.enums import ModuloSistema


class PermissaoUpdate(BaseModel):
    pode_visualizar: bool | None = None
    pode_editar: bool | None = None
    pode_excluir: bool | None = None


class PermissaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    modulo: ModuloSistema
    pode_visualizar: bool
    pode_editar: bool
    pode_excluir: bool
