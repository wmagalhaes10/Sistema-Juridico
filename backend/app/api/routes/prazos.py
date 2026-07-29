import uuid
from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permissao
from app.core.database import get_db
from app.models.enums import ModuloSistema, StatusPrazo
from app.models.prazo import Prazo
from app.schemas.prazo import DashboardPrazos, PrazoListResponse, PrazoRead, PrazoUpdate
from app.services import prazo_service

router = APIRouter(prefix="/prazos", tags=["prazos"])


async def _get_prazo_or_404(prazo_id: uuid.UUID, db: AsyncSession) -> Prazo:
    prazo = await prazo_service.get_by_id(db, prazo_id)
    if prazo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prazo não encontrado")
    return prazo


@router.get(
    "",
    response_model=PrazoListResponse,
    dependencies=[Depends(require_permissao(ModuloSistema.PRAZOS, "visualizar"))],
)
async def list_prazos(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 50,
    processo_id: uuid.UUID | None = None,
    responsavel_id: uuid.UUID | None = None,
    status_prazo: StatusPrazo | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> PrazoListResponse:
    items, total = await prazo_service.list_prazos(
        db, page=page, page_size=page_size, processo_id=processo_id,
        responsavel_id=responsavel_id, status=status_prazo,
        data_inicio=data_inicio, data_fim=data_fim,
    )
    return PrazoListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/dashboard",
    response_model=DashboardPrazos,
    dependencies=[Depends(require_permissao(ModuloSistema.PRAZOS, "visualizar"))],
)
async def dashboard_prazos(
    db: Annotated[AsyncSession, Depends(get_db)],
    visao: Literal["semanal", "mensal"] = "semanal",
    referencia: date | None = None,
) -> DashboardPrazos:
    ref = referencia or date.today()
    resultado = await prazo_service.dashboard(db, visao, ref)
    return DashboardPrazos(**resultado)


@router.get(
    "/{prazo_id}",
    response_model=PrazoRead,
    dependencies=[Depends(require_permissao(ModuloSistema.PRAZOS, "visualizar"))],
)
async def get_prazo(prazo_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> Prazo:
    return await _get_prazo_or_404(prazo_id, db)


@router.patch(
    "/{prazo_id}",
    response_model=PrazoRead,
    dependencies=[Depends(require_permissao(ModuloSistema.PRAZOS, "editar"))],
)
async def update_prazo(
    prazo_id: uuid.UUID,
    data: PrazoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Prazo:
    prazo = await _get_prazo_or_404(prazo_id, db)
    return await prazo_service.update_prazo(db, prazo, data)


@router.delete(
    "/{prazo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permissao(ModuloSistema.PRAZOS, "excluir"))],
)
async def delete_prazo(prazo_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    prazo = await _get_prazo_or_404(prazo_id, db)
    await prazo_service.delete_prazo(db, prazo)
