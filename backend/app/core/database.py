import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Em ambiente serverless (Vercel), cada invocação deve abrir e fechar sua própria
# conexão (NullPool) e o cache de prepared statements do asyncpg precisa ser
# desativado, pois o pooler do Supabase (pgbouncer) não os suporta entre transações.
_IS_SERVERLESS = bool(os.environ.get("VERCEL"))

if _IS_SERVERLESS:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        poolclass=NullPool,
        connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0},
    )
else:
    engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
