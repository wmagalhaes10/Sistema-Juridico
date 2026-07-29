import uuid

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.permissao import PermissaoRead


class UserBase(BaseModel):
    nome: str
    email: EmailStr
    oab: str | None = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ativo: bool
    super_admin: bool
    permissoes: list[PermissaoRead] = []


class UserUpdate(BaseModel):
    nome: str | None = None
    oab: str | None = None
    ativo: bool | None = None


class UsuarioBasico(BaseModel):
    """Versão enxuta para seletores de responsável — não exige ser super_admin para consultar."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    ativo: bool
