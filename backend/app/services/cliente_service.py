import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate


async def get_by_id(db: AsyncSession, cliente_id: uuid.UUID) -> Cliente | None:
    return await db.get(Cliente, cliente_id)


async def get_by_cpf_cnpj(db: AsyncSession, cpf_cnpj: str) -> Cliente | None:
    result = await db.execute(select(Cliente).where(Cliente.cpf_cnpj == cpf_cnpj))
    return result.scalar_one_or_none()


async def list_clientes(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    busca: str | None = None,
) -> tuple[list[Cliente], int]:
    query = select(Cliente)
    if busca:
        termo = f"%{busca}%"
        query = query.where(
            or_(Cliente.nome_razao_social.ilike(termo), Cliente.cpf_cnpj.like(f"%{busca}%"))
        )

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()

    result = await db.execute(
        query.order_by(Cliente.nome_razao_social).offset((page - 1) * page_size).limit(page_size)
    )
    return list(result.scalars().all()), total


async def create_cliente(db: AsyncSession, data: ClienteCreate) -> Cliente:
    cliente = Cliente(**data.model_dump())
    db.add(cliente)
    await db.commit()
    await db.refresh(cliente)
    return cliente


async def update_cliente(db: AsyncSession, cliente: Cliente, data: ClienteUpdate) -> Cliente:
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)
    await db.commit()
    await db.refresh(cliente)
    return cliente


async def delete_cliente(db: AsyncSession, cliente: Cliente) -> None:
    await db.delete(cliente)
    await db.commit()
