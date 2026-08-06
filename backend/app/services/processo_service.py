import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import FaseProcessual, OrigemMovimentacao, StatusProcesso
from app.models.movimentacao import Movimentacao
from app.models.processo import Processo
from app.schemas.processo import MovimentacaoCreate, ProcessoCreate, ProcessoUpdate


async def get_by_id(db: AsyncSession, processo_id: uuid.UUID) -> Processo | None:
    result = await db.execute(
        select(Processo).where(Processo.id == processo_id).options(selectinload(Processo.cliente))
    )
    return result.scalar_one_or_none()


async def get_by_numero_cnj(db: AsyncSession, numero_cnj: str) -> Processo | None:
    result = await db.execute(select(Processo).where(Processo.numero_cnj == numero_cnj))
    return result.scalar_one_or_none()


async def list_processos(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    busca: str | None = None,
    status: StatusProcesso | None = None,
    fase: FaseProcessual | None = None,
    cliente_id: uuid.UUID | None = None,
) -> tuple[list[Processo], int]:
    query = select(Processo)
    if busca:
        termo = f"%{busca}%"
        query = query.where(
            or_(
                Processo.numero_cnj.like(f"%{busca}%"),
                Processo.polo_ativo.ilike(termo),
                Processo.polo_passivo.ilike(termo),
                Processo.tipo_acao.ilike(termo),
            )
        )
    if status is not None:
        query = query.where(Processo.status == status)
    if fase is not None:
        query = query.where(Processo.fase_processual == fase)
    if cliente_id is not None:
        query = query.where(Processo.cliente_id == cliente_id)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()

    result = await db.execute(
        query.options(selectinload(Processo.cliente))
        .order_by(Processo.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(result.scalars().all()), total


async def create_processo(db: AsyncSession, data: ProcessoCreate) -> Processo:
    processo = Processo(**data.model_dump())
    db.add(processo)
    await db.commit()
    return await get_by_id(db, processo.id)


async def update_processo(db: AsyncSession, processo: Processo, data: ProcessoUpdate) -> Processo:
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(processo, campo, valor)
    await db.commit()
    return await get_by_id(db, processo.id)


async def delete_processo(db: AsyncSession, processo: Processo) -> None:
    await db.delete(processo)
    await db.commit()


async def list_movimentacoes(db: AsyncSession, processo_id: uuid.UUID) -> list[Movimentacao]:
    result = await db.execute(
        select(Movimentacao)
        .where(Movimentacao.processo_id == processo_id)
        .order_by(Movimentacao.data_movimentacao.desc())
    )
    return list(result.scalars().all())


async def create_movimentacao(
    db: AsyncSession,
    processo_id: uuid.UUID,
    data: MovimentacaoCreate,
    origem: OrigemMovimentacao = OrigemMovimentacao.MANUAL,
) -> Movimentacao:
    movimentacao = Movimentacao(processo_id=processo_id, origem=origem, **data.model_dump())
    db.add(movimentacao)
    await db.commit()
    await db.refresh(movimentacao)
    return movimentacao
