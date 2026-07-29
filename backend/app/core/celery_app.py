from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "sistema_juridico",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.sincronizacao", "app.tasks.alertas", "app.tasks.publicacoes"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "sincronizar-publicacoes-djen-diario": {
        "task": "app.tasks.publicacoes.sincronizar_publicacoes_djen",
        "schedule": crontab(hour=6, minute=30),
    },
    "sincronizar-processos-datajud-diario": {
        "task": "app.tasks.sincronizacao.sincronizar_todos_processos_ativos",
        "schedule": crontab(hour=7, minute=0),
    },
    "verificar-prazos-e-enviar-alertas-diario": {
        "task": "app.tasks.alertas.verificar_prazos_e_enviar_alertas",
        "schedule": crontab(hour=7, minute=15),
    },
}
