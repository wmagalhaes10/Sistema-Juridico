import uuid
from decimal import Decimal

from pydantic import BaseModel


class SaldoProcesso(BaseModel):
    processo_id: uuid.UUID
    total_receitas: Decimal
    total_despesas: Decimal
    saldo: Decimal


class RelatorioReceitas(BaseModel):
    total: Decimal
    quantidade_parcelas: int


class RelatorioDespesas(BaseModel):
    total: Decimal
    quantidade: int
