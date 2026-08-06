import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ModuloSistema
from app.models.permissao import Permissao
from app.schemas.permissao import PermissaoUpdate


async def get(db: AsyncSession, user_id: uuid.UUID, modulo: ModuloSistema) -> Permissao | None:
    result = await db.execute(select(Permissao).where(Permissao.user_id == user_id, Permissao.modulo == modulo))
    return result.scalar_one_or_none()


async def update(db: AsyncSession, permissao: Permissao, data: PermissaoUpdate) -> Permissao:
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(permissao, campo, valor)
    await db.commit()
    await db.refresh(permissao)
    return permissao
