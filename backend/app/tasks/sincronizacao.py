import asyncio
import logging

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.enums import StatusProcesso
from app.models.processo import Processo
from app.services.sincronizacao_service import sincronizar_processo

logger = logging.getLogger(__name__)


async def _executar() -> int:
    total_sincronizados = 0
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Processo).where(Processo.status == StatusProcesso.ATIVO))
        processos = list(result.scalars().all())

        for processo in processos:
            try:
                await sincronizar_processo(db, processo)
                total_sincronizados += 1
            except Exception:
                logger.exception("Falha ao sincronizar processo %s com o DataJud", processo.numero_cnj)
                await db.rollback()

    return total_sincronizados


@celery_app.task(name="app.tasks.sincronizacao.sincronizar_todos_processos_ativos")
def sincronizar_todos_processos_ativos() -> int:
    return asyncio.run(_executar())
