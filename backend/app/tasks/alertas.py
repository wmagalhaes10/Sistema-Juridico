import asyncio
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.enums import StatusPrazo
from app.models.prazo import Prazo
from app.models.user import User
from app.services.email_service import enviar_email

# antecedência (em dias) configurável para disparo dos alertas de prazo
ANTECEDENCIAS_DIAS = (3, 5, 10)


async def _prazos_para_alertar(db: AsyncSession) -> list[Prazo]:
    hoje = date.today()
    datas_alvo = [hoje + timedelta(days=d) for d in ANTECEDENCIAS_DIAS]
    result = await db.execute(
        select(Prazo)
        .where(Prazo.status == StatusPrazo.PENDENTE, Prazo.data_prazo.in_(datas_alvo))
        .options(selectinload(Prazo.processo), selectinload(Prazo.responsavel))
    )
    return list(result.scalars().all())


async def _destinatario(db: AsyncSession, prazo: Prazo) -> str | None:
    if prazo.responsavel is not None:
        return prazo.responsavel.email
    if prazo.processo.advogado_responsavel_id is not None:
        advogado = await db.get(User, prazo.processo.advogado_responsavel_id)
        return advogado.email if advogado else None
    return None


async def _executar() -> int:
    enviados = 0
    async with AsyncSessionLocal() as db:
        for prazo in await _prazos_para_alertar(db):
            destinatario = await _destinatario(db, prazo)
            if not destinatario:
                continue

            dias_restantes = (prazo.data_prazo - date.today()).days
            assunto = f"[Prazo em {dias_restantes} dia(s)] Processo {prazo.processo.numero_cnj}"
            corpo = (
                f"<p>O prazo do tipo <b>{prazo.tipo.value}</b> do processo "
                f"<b>{prazo.processo.numero_cnj}</b> vence em {dias_restantes} dia(s), "
                f"em {prazo.data_prazo.strftime('%d/%m/%Y')}.</p>"
                f"<p>{prazo.descricao or ''}</p>"
            )
            enviar_email(destinatario, assunto, corpo)
            enviados += 1
    return enviados


@celery_app.task(name="app.tasks.alertas.verificar_prazos_e_enviar_alertas")
def verificar_prazos_e_enviar_alertas() -> int:
    return asyncio.run(_executar())
