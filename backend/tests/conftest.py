import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import *  # noqa: F401,F403 garante que todos os models sejam registrados


@pytest_asyncio.fixture
async def session_maker():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db():
        async with maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield maker

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session_maker):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def criar_usuario(session_maker, email, password, super_admin=False):
    from app.core.security import hash_password
    from app.models.enums import ModuloSistema
    from app.models.permissao import Permissao
    from app.models.user import User

    async with session_maker() as session:
        user = User(nome="Teste", email=email, hashed_password=hash_password(password), super_admin=super_admin)
        session.add(user)
        await session.flush()

        if not super_admin:
            for modulo in ModuloSistema:
                session.add(Permissao(user_id=user.id, modulo=modulo))

        await session.commit()
        await session.refresh(user)
        return user


async def restringir_permissao(session_maker, user_id, modulo, **flags):
    """Ajusta pode_visualizar/pode_editar/pode_excluir de um módulo específico para um funcionário."""
    import uuid as uuid_mod

    from app.models.permissao import Permissao

    if isinstance(user_id, str):
        user_id = uuid_mod.UUID(user_id)

    async with session_maker() as session:
        result = await session.execute(
            select(Permissao).where(Permissao.user_id == user_id, Permissao.modulo == modulo)
        )
        permissao = result.scalar_one()
        for campo, valor in flags.items():
            setattr(permissao, campo, valor)
        await session.commit()


async def auth_headers(client, session_maker, email, super_admin=False):
    await criar_usuario(session_maker, email, "senha123", super_admin=super_admin)
    login = await client.post("/auth/login", data={"username": email, "password": "senha123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client, session_maker):
    """Super admin: acesso total e irrestrito, não passa pelas permissões."""
    return await auth_headers(client, session_maker, "admin@example.com", super_admin=True)


@pytest_asyncio.fixture
async def funcionario_headers(client, session_maker):
    """Funcionário comum: nasce com acesso total (todas as permissões liberadas por padrão)."""
    return await auth_headers(client, session_maker, "funcionario@example.com")
