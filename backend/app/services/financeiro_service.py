import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contrato_honorario import ContratoHonorario
from app.models.despesa import Despesa
from app.models.parcela_honorario import ParcelaHonorario


async def saldo_processo(db: AsyncSession, processo_id: uuid.UUID) -> dict:
    receitas_result = await db.execute(
        select(func.coalesce(func.sum(ParcelaHonorario.valor), 0))
        .join(ContratoHonorario, ParcelaHonorario.contrato_id == ContratoHonorario.id)
        .where(ContratoHonorario.processo_id == processo_id, ParcelaHonorario.data_pagamento.is_not(None))
    )
    total_receitas = receitas_result.scalar_one()

    despesas_result = await db.execute(
        select(func.coalesce(func.sum(Despesa.valor), 0)).where(Despesa.processo_id == processo_id)
    )
    total_despesas = despesas_result.scalar_one()

    return {
        "processo_id": processo_id,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": total_receitas - total_despesas,
    }


async def relatorio_receitas(
    db: AsyncSession,
    cliente_id: uuid.UUID | None = None,
    processo_id: uuid.UUID | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> dict:
    query = (
        select(func.coalesce(func.sum(ParcelaHonorario.valor), 0), func.count(ParcelaHonorario.id))
        .join(ContratoHonorario, ParcelaHonorario.contrato_id == ContratoHonorario.id)
        .where(ParcelaHonorario.data_pagamento.is_not(None))
    )
    if cliente_id is not None:
        query = query.where(ContratoHonorario.cliente_id == cliente_id)
    if processo_id is not None:
        query = query.where(ContratoHonorario.processo_id == processo_id)
    if data_inicio is not None:
        query = query.where(ParcelaHonorario.data_pagamento >= data_inicio)
    if data_fim is not None:
        query = query.where(ParcelaHonorario.data_pagamento <= data_fim)

    total, quantidade = (await db.execute(query)).one()
    return {"total": total, "quantidade_parcelas": quantidade}


async def relatorio_despesas(
    db: AsyncSession,
    processo_id: uuid.UUID | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> dict:
    query = select(func.coalesce(func.sum(Despesa.valor), 0), func.count(Despesa.id))
    if processo_id is not None:
        query = query.where(Despesa.processo_id == processo_id)
    if data_inicio is not None:
        query = query.where(Despesa.data_despesa >= data_inicio)
    if data_fim is not None:
        query = query.where(Despesa.data_despesa <= data_fim)

    total, quantidade = (await db.execute(query)).one()
    return {"total": total, "quantidade": quantidade}
