import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import StatusTarefa
from app.models.tarefa import Tarefa
from app.schemas.tarefa import TarefaCreate, TarefaUpdate


async def get_by_id(db: AsyncSession, tarefa_id: uuid.UUID) -> Tarefa | None:
    result = await db.execute(
        select(Tarefa)
        .where(Tarefa.id == tarefa_id)
        .options(selectinload(Tarefa.responsavel), selectinload(Tarefa.processo))
    )
    return result.scalar_one_or_none()


async def list_tarefas(
    db: AsyncSession,
    responsavel_id: uuid.UUID | None = None,
    status: StatusTarefa | None = None,
    processo_id: uuid.UUID | None = None,
) -> list[Tarefa]:
    query = select(Tarefa).options(selectinload(Tarefa.responsavel), selectinload(Tarefa.processo))
    if responsavel_id is not None:
        query = query.where(Tarefa.responsavel_id == responsavel_id)
    if status is not None:
        query = query.where(Tarefa.status == status)
    if processo_id is not None:
        query = query.where(Tarefa.processo_id == processo_id)

    # tarefas sem data de vencimento vão para o final da lista
    result = await db.execute(query.order_by(Tarefa.data_vencimento.is_(None), Tarefa.data_vencimento))
    return list(result.scalars().all())


async def create_tarefa(db: AsyncSession, data: TarefaCreate, criado_por_id: uuid.UUID) -> Tarefa:
    tarefa = Tarefa(**data.model_dump(), criado_por_id=criado_por_id)
    db.add(tarefa)
    await db.commit()
    return await get_by_id(db, tarefa.id)


async def update_tarefa(db: AsyncSession, tarefa: Tarefa, data: TarefaUpdate) -> Tarefa:
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(tarefa, campo, valor)
    await db.commit()
    return await get_by_id(db, tarefa.id)


async def delete_tarefa(db: AsyncSession, tarefa: Tarefa) -> None:
    await db.delete(tarefa)
    await db.commit()
