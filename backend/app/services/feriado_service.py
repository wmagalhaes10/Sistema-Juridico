from datetime import date, timedelta

import httpx
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.enums import TipoFeriado
from app.models.feriado import Feriado


async def sincronizar_feriados(
    db: AsyncSession, ano: int, client: httpx.AsyncClient | None = None
) -> list[Feriado]:
    """Busca os feriados nacionais do ano na BrasilAPI e grava os que ainda não existem."""
    fechar_cliente = client is None
    client = client or httpx.AsyncClient(timeout=10)
    try:
        response = await client.get(f"{settings.BRASILAPI_FERIADOS_URL}/{ano}")
        response.raise_for_status()
        dados = response.json()
    finally:
        if fechar_cliente:
            await client.aclose()

    criados: list[Feriado] = []
    for item in dados:
        data_feriado = date.fromisoformat(item["date"])
        existente = await db.execute(select(Feriado).where(Feriado.data == data_feriado, Feriado.uf.is_(None)))
        if existente.scalar_one_or_none() is not None:
            continue
        feriado = Feriado(data=data_feriado, nome=item["name"], tipo=TipoFeriado.NACIONAL, uf=None)
        db.add(feriado)
        criados.append(feriado)

    await db.commit()
    return criados


async def list_feriados(db: AsyncSession, ano: int | None = None, uf: str | None = None) -> list[Feriado]:
    query = select(Feriado)
    if ano is not None:
        query = query.where(Feriado.data >= date(ano, 1, 1), Feriado.data <= date(ano, 12, 31))
    if uf is not None:
        query = query.where(Feriado.uf == uf)
    result = await db.execute(query.order_by(Feriado.data))
    return list(result.scalars().all())


async def is_dia_util(db: AsyncSession, dia: date, uf: str | None = None) -> bool:
    if dia.weekday() >= 5:  # sábado ou domingo
        return False

    filtro_uf = or_(Feriado.uf.is_(None), Feriado.uf == uf) if uf else Feriado.uf.is_(None)
    result = await db.execute(select(Feriado).where(Feriado.data == dia).where(filtro_uf))
    return result.scalar_one_or_none() is None


async def adicionar_dias_uteis(db: AsyncSession, data_inicial: date, dias: int, uf: str | None = None) -> date:
    atual = data_inicial
    contados = 0
    while contados < dias:
        atual += timedelta(days=1)
        if await is_dia_util(db, atual, uf):
            contados += 1
    return atual
