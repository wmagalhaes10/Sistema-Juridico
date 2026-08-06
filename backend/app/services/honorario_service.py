import calendar
import uuid
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.contrato_honorario import ContratoHonorario
from app.models.enums import StatusParcela
from app.models.parcela_honorario import ParcelaHonorario
from app.schemas.contrato_honorario import ContratoHonorarioCreate
from app.schemas.parcela import ParcelaUpdate


def _soma_meses(d: date, meses: int) -> date:
    mes_total = d.month - 1 + meses
    ano = d.year + mes_total // 12
    mes = mes_total % 12 + 1
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    return date(ano, mes, min(d.day, ultimo_dia))


async def get_by_id(db: AsyncSession, contrato_id: uuid.UUID) -> ContratoHonorario | None:
    result = await db.execute(
        select(ContratoHonorario)
        .where(ContratoHonorario.id == contrato_id)
        .options(selectinload(ContratoHonorario.parcelas))
    )
    return result.scalar_one_or_none()


async def list_contratos(
    db: AsyncSession,
    cliente_id: uuid.UUID | None = None,
    processo_id: uuid.UUID | None = None,
) -> list[ContratoHonorario]:
    query = select(ContratoHonorario).options(selectinload(ContratoHonorario.parcelas))
    if cliente_id is not None:
        query = query.where(ContratoHonorario.cliente_id == cliente_id)
    if processo_id is not None:
        query = query.where(ContratoHonorario.processo_id == processo_id)
    result = await db.execute(query.order_by(ContratoHonorario.created_at.desc()))
    return list(result.scalars().all())


async def create_contrato(db: AsyncSession, data: ContratoHonorarioCreate) -> ContratoHonorario:
    contrato = ContratoHonorario(
        cliente_id=data.cliente_id,
        processo_id=data.processo_id,
        tipo=data.tipo,
        valor_contratado=data.valor_contratado,
        numero_parcelas=data.numero_parcelas,
        data_assinatura=data.data_assinatura,
        observacoes=data.observacoes,
    )
    db.add(contrato)
    await db.flush()

    base = data.data_assinatura or date.today()
    valor_parcela = (data.valor_contratado / data.numero_parcelas).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    valor_ultima = data.valor_contratado - valor_parcela * (data.numero_parcelas - 1)

    for i in range(data.numero_parcelas):
        valor = valor_parcela if i < data.numero_parcelas - 1 else valor_ultima
        vencimento = base if data.numero_parcelas == 1 else _soma_meses(base, i + 1)
        db.add(
            ParcelaHonorario(
                contrato_id=contrato.id,
                numero_parcela=i + 1,
                valor=valor,
                data_vencimento=vencimento,
            )
        )

    await db.commit()
    return await get_by_id(db, contrato.id)


async def get_parcela(db: AsyncSession, parcela_id: uuid.UUID) -> ParcelaHonorario | None:
    return await db.get(ParcelaHonorario, parcela_id)


async def get_parcela_com_relacionamentos(db: AsyncSession, parcela_id: uuid.UUID) -> ParcelaHonorario | None:
    result = await db.execute(
        select(ParcelaHonorario)
        .where(ParcelaHonorario.id == parcela_id)
        .options(selectinload(ParcelaHonorario.contrato).selectinload(ContratoHonorario.cliente))
    )
    return result.scalar_one_or_none()


async def update_parcela(db: AsyncSession, parcela: ParcelaHonorario, data: ParcelaUpdate) -> ParcelaHonorario:
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(parcela, campo, valor)
    parcela.status = StatusParcela.PAGO if parcela.data_pagamento is not None else StatusParcela.PENDENTE
    await db.commit()
    await db.refresh(parcela)
    return parcela


async def registrar_pagamento(
    db: AsyncSession, parcela: ParcelaHonorario, data_pagamento: date | None = None
) -> ParcelaHonorario:
    parcela.data_pagamento = data_pagamento or date.today()
    parcela.status = StatusParcela.PAGO
    await db.commit()
    await db.refresh(parcela)
    return parcela
