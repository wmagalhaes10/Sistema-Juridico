import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password, verify_password
from app.models.enums import ModuloSistema
from app.models.permissao import Permissao
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await db.get(User, user_id)


async def get_by_id_com_permissoes(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id).options(selectinload(User.permissoes)))
    return result.scalar_one_or_none()


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def list_funcionarios(db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(User).where(User.super_admin.is_(False)).options(selectinload(User.permissoes)).order_by(User.nome)
    )
    return list(result.scalars().all())


async def list_ativos_basico(db: AsyncSession) -> list[User]:
    """Lista enxuta (sem permissões) para seletores de responsável — qualquer usuário autenticado pode ver."""
    result = await db.execute(select(User).where(User.ativo.is_(True)).order_by(User.nome))
    return list(result.scalars().all())


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """Cria um funcionário. Nasce com acesso total (todas as permissões liberadas);
    o super_admin pode restringir depois em módulo a módulo."""
    user = User(
        nome=data.nome,
        email=data.email,
        hashed_password=hash_password(data.password),
        oab=data.oab,
        super_admin=False,
    )
    db.add(user)
    await db.flush()

    for modulo in ModuloSistema:
        db.add(Permissao(user_id=user.id, modulo=modulo))

    await db.commit()
    return await get_by_id_com_permissoes(db, user.id)


async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(user, campo, valor)
    await db.commit()
    return await get_by_id_com_permissoes(db, user.id)


async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
