import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permissao
from app.core.database import get_db
from app.models.enums import ModuloSistema
from app.schemas.feriado import FeriadoRead
from app.schemas.processo import MovimentacaoRead
from app.services import feriado_service, processo_service, sincronizacao_service
from app.services.datajud_service import DataJudError

router = APIRouter(tags=["integracoes"])


@router.post(
    "/feriados/sincronizar/{ano}",
    response_model=list[FeriadoRead],
    dependencies=[Depends(require_permissao(ModuloSistema.PRAZOS, "editar"))],
)
async def sincronizar_feriados(ano: int, db: Annotated[AsyncSession, Depends(get_db)]) -> list[FeriadoRead]:
    return await feriado_service.sincronizar_feriados(db, ano)


@router.get(
    "/feriados",
    response_model=list[FeriadoRead],
    dependencies=[Depends(require_permissao(ModuloSistema.PRAZOS, "visualizar"))],
)
async def list_feriados(
    db: Annotated[AsyncSession, Depends(get_db)],
    ano: int | None = None,
    uf: str | None = None,
) -> list[FeriadoRead]:
    return await feriado_service.list_feriados(db, ano=ano, uf=uf)


@router.post(
    "/processos/{processo_id}/sincronizar-datajud",
    response_model=list[MovimentacaoRead],
    dependencies=[Depends(require_permissao(ModuloSistema.PROCESSOS, "editar"))],
)
async def sincronizar_datajud(
    processo_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]
) -> list[MovimentacaoRead]:
    processo = await processo_service.get_by_id(db, processo_id)
    if processo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processo não encontrado")
    try:
        return await sincronizacao_service.sincronizar_processo(db, processo)
    except DataJudError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
