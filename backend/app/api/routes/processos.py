import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permissao
from app.core.database import get_db
from app.models.enums import FaseProcessual, ModuloSistema, StatusProcesso
from app.models.processo import Processo
from app.schemas.prazo import PrazoCreate, PrazoRead
from app.schemas.processo import (
    MovimentacaoCreate,
    MovimentacaoRead,
    ProcessoCreate,
    ProcessoListResponse,
    ProcessoRead,
    ProcessoUpdate,
)
from app.services import cliente_service, prazo_service, processo_service

router = APIRouter(prefix="/processos", tags=["processos"])


async def _get_processo_or_404(processo_id: uuid.UUID, db: AsyncSession) -> Processo:
    processo = await processo_service.get_by_id(db, processo_id)
    if processo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processo não encontrado")
    return processo


@router.get(
    "",
    response_model=ProcessoListResponse,
    dependencies=[Depends(require_permissao(ModuloSistema.PROCESSOS, "visualizar"))],
)
async def list_processos(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    busca: str | None = None,
    status_processo: StatusProcesso | None = None,
    fase: FaseProcessual | None = None,
    cliente_id: uuid.UUID | None = None,
) -> ProcessoListResponse:
    items, total = await processo_service.list_processos(
        db, page=page, page_size=page_size, busca=busca,
        status=status_processo, fase=fase, cliente_id=cliente_id,
    )
    return ProcessoListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/{processo_id}",
    response_model=ProcessoRead,
    dependencies=[Depends(require_permissao(ModuloSistema.PROCESSOS, "visualizar"))],
)
async def get_processo(processo_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> Processo:
    return await _get_processo_or_404(processo_id, db)


@router.post(
    "",
    response_model=ProcessoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissao(ModuloSistema.PROCESSOS, "editar"))],
)
async def create_processo(data: ProcessoCreate, db: Annotated[AsyncSession, Depends(get_db)]) -> Processo:
    if await processo_service.get_by_numero_cnj(db, data.numero_cnj) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Processo já cadastrado")
    if await cliente_service.get_by_id(db, data.cliente_id) is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cliente não encontrado")
    try:
        return await processo_service.create_processo(db, data)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Processo já cadastrado")


@router.put(
    "/{processo_id}",
    response_model=ProcessoRead,
    dependencies=[Depends(require_permissao(ModuloSistema.PROCESSOS, "editar"))],
)
async def update_processo(
    processo_id: uuid.UUID,
    data: ProcessoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Processo:
    processo = await _get_processo_or_404(processo_id, db)
    return await processo_service.update_processo(db, processo, data)


@router.delete(
    "/{processo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permissao(ModuloSistema.PROCESSOS, "excluir"))],
)
async def delete_processo(processo_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    processo = await _get_processo_or_404(processo_id, db)
    try:
        await processo_service.delete_processo(db, processo)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Processo possui contratos de honorários vinculados e não pode ser excluído",
        )


@router.get(
    "/{processo_id}/movimentacoes",
    response_model=list[MovimentacaoRead],
    dependencies=[Depends(require_permissao(ModuloSistema.PROCESSOS, "visualizar"))],
)
async def list_movimentacoes(processo_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    await _get_processo_or_404(processo_id, db)
    return await processo_service.list_movimentacoes(db, processo_id)


@router.post(
    "/{processo_id}/movimentacoes",
    response_model=MovimentacaoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissao(ModuloSistema.PROCESSOS, "editar"))],
)
async def create_movimentacao(
    processo_id: uuid.UUID,
    data: MovimentacaoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _get_processo_or_404(processo_id, db)
    return await processo_service.create_movimentacao(db, processo_id, data)


@router.get(
    "/{processo_id}/prazos",
    response_model=list[PrazoRead],
    dependencies=[Depends(require_permissao(ModuloSistema.PRAZOS, "visualizar"))],
)
async def list_prazos_do_processo(processo_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    await _get_processo_or_404(processo_id, db)
    items, _ = await prazo_service.list_prazos(db, processo_id=processo_id, page_size=200)
    return items


@router.post(
    "/{processo_id}/prazos",
    response_model=PrazoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissao(ModuloSistema.PRAZOS, "editar"))],
)
async def create_prazo(
    processo_id: uuid.UUID,
    data: PrazoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _get_processo_or_404(processo_id, db)
    return await prazo_service.create_prazo(db, processo_id, data)
