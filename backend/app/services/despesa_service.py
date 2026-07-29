import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.despesa import Despesa
from app.schemas.despesa import DespesaCreate


async def list_despesas(
    db: AsyncSession,
    processo_id: uuid.UUID | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[Despesa]:
    query = select(Despesa)
    if processo_id is not None:
        query = query.where(Despesa.processo_id == processo_id)
    if data_inicio is not None:
        query = query.where(Despesa.data_despesa >= data_inicio)
    if data_fim is not None:
        query = query.where(Despesa.data_despesa <= data_fim)

    result = await db.execute(query.order_by(Despesa.data_despesa.desc()))
    return list(result.scalars().all())


async def create_despesa(db: AsyncSession, processo_id: uuid.UUID, data: DespesaCreate) -> Despesa:
    despesa = Despesa(processo_id=processo_id, **data.model_dump())
    db.add(despesa)
    await db.commit()
    await db.refresh(despesa)
    return despesa
