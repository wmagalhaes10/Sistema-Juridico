import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator

from app.core.validators import cnpj_valido, cpf_valido, somente_digitos
from app.models.enums import TipoPessoa


class ClienteBase(BaseModel):
    tipo_pessoa: TipoPessoa
    cpf_cnpj: str
    nome_razao_social: str
    endereco: str | None = None
    telefone: str | None = None
    email: EmailStr | None = None
    oab_responsavel: str | None = None

    @field_validator("cpf_cnpj")
    @classmethod
    def normaliza_cpf_cnpj(cls, v: str) -> str:
        return somente_digitos(v)

    @model_validator(mode="after")
    def valida_documento(self) -> "ClienteBase":
        if self.tipo_pessoa == TipoPessoa.FISICA and not cpf_valido(self.cpf_cnpj):
            raise ValueError("CPF inválido")
        if self.tipo_pessoa == TipoPessoa.JURIDICA and not cnpj_valido(self.cpf_cnpj):
            raise ValueError("CNPJ inválido")
        return self


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome_razao_social: str | None = None
    endereco: str | None = None
    telefone: str | None = None
    email: EmailStr | None = None
    oab_responsavel: str | None = None


class ClienteRead(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class ClienteListResponse(BaseModel):
    items: list[ClienteRead]
    total: int
    page: int
    page_size: int
