import asyncio
import logging

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.publicacao_service import sincronizar

logger = logging.getLogger(__name__)


async def _executar() -> int:
    async with AsyncSessionLocal() as db:
        try:
            novas = await sincronizar(db)
        except Exception:
            logger.exception("Falha ao sincronizar publicações do DJEN")
            await db.rollback()
            return 0
    return len(novas)


@celery_app.task(name="app.tasks.publicacoes.sincronizar_publicacoes_djen")
def sincronizar_publicacoes_djen() -> int:
    return asyncio.run(_executar())
