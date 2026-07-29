import uuid
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import StatusPrazo
from app.models.prazo import Prazo
from app.schemas.prazo import PrazoCreate, PrazoUpdate


async def get_by_id(db: AsyncSession, prazo_id: uuid.UUID) -> Prazo | None:
    result = await db.execute(
        select(Prazo).where(Prazo.id == prazo_id).options(selectinload(Prazo.processo))
    )
    return result.scalar_one_or_none()


async def list_prazos(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    processo_id: uuid.UUID | None = None,
    responsavel_id: uuid.UUID | None = None,
    status: StatusPrazo | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> tuple[list[Prazo], int]:
    query = select(Prazo)
    if processo_id is not None:
        query = query.where(Prazo.processo_id == processo_id)
    if responsavel_id is not None:
        query = query.where(Prazo.responsavel_id == responsavel_id)
    if status is not None:
        query = query.where(Prazo.status == status)
    if data_inicio is not None:
        query = query.where(Prazo.data_prazo >= data_inicio)
    if data_fim is not None:
        query = query.where(Prazo.data_prazo <= data_fim)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()

    result = await db.execute(
        query.options(selectinload(Prazo.processo))
        .order_by(Prazo.data_prazo)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(result.scalars().all()), total


async def create_prazo(db: AsyncSession, processo_id: uuid.UUID, data: PrazoCreate) -> Prazo:
    prazo = Prazo(processo_id=processo_id, **data.model_dump())
    db.add(prazo)
    await db.commit()
    return await get_by_id(db, prazo.id)


async def update_prazo(db: AsyncSession, prazo: Prazo, data: PrazoUpdate) -> Prazo:
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(prazo, campo, valor)
    await db.commit()
    return await get_by_id(db, prazo.id)


async def delete_prazo(db: AsyncSession, prazo: Prazo) -> None:
    await db.delete(prazo)
    await db.commit()


def janela_dashboard(visao: str, referencia: date) -> tuple[date, date]:
    if visao == "semanal":
        inicio = referencia - timedelta(days=referencia.weekday())  # segunda-feira
        fim = inicio + timedelta(days=6)
    else:  # mensal
        inicio = referencia.replace(day=1)
        if inicio.month == 12:
            fim = inicio.replace(year=inicio.year + 1, month=1) - timedelta(days=1)
        else:
            fim = inicio.replace(month=inicio.month + 1) - timedelta(days=1)
    return inicio, fim


async def dashboard(db: AsyncSession, visao: str, referencia: date) -> dict:
    inicio, fim = janela_dashboard(visao, referencia)

    prazos, _ = await list_prazos(db, page_size=500, data_inicio=inicio, data_fim=fim)

    total_pendentes = sum(1 for p in prazos if p.status == StatusPrazo.PENDENTE)
    vencidos_result = await db.execute(
        select(func.count())
        .select_from(Prazo)
        .where(Prazo.status == StatusPrazo.PENDENTE, Prazo.data_prazo < referencia)
    )
    vencidos = vencidos_result.scalar_one()

    return {
        "inicio": inicio,
        "fim": fim,
        "total_pendentes": total_pendentes,
        "vencidos": vencidos,
        "prazos": prazos,
    }
