import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permissao
from app.core.database import get_db
from app.models.enums import ModuloSistema, StatusPublicacao
from app.models.user import User
from app.schemas.publicacao import (
    PublicacaoListResponse,
    PublicacaoRead,
    PublicacaoStatusUpdate,
    PublicacoesResumo,
)
from app.services import publicacao_service
from app.services.djen_service import DjenError

router = APIRouter(prefix="/publicacoes", tags=["publicacoes"])

_visualizar = Depends(require_permissao(ModuloSistema.PUBLICACOES, "visualizar"))
_editar = Depends(require_permissao(ModuloSistema.PUBLICACOES, "editar"))


@router.get("", response_model=PublicacaoListResponse, dependencies=[_visualizar])
async def list_publicacoes(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status_publicacao: StatusPublicacao | None = None,
    sigla_tribunal: str | None = None,
    processo_id: uuid.UUID | None = None,
) -> PublicacaoListResponse:
    items, total = await publicacao_service.list_publicacoes(
        db, page=page, page_size=page_size, status=status_publicacao,
        sigla_tribunal=sigla_tribunal, processo_id=processo_id,
    )
    return PublicacaoListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/resumo", response_model=PublicacoesResumo, dependencies=[_visualizar])
async def resumo_publicacoes(db: Annotated[AsyncSession, Depends(get_db)]) -> PublicacoesResumo:
    return PublicacoesResumo(**await publicacao_service.resumo(db))


@router.post("/sincronizar", response_model=list[PublicacaoRead], dependencies=[_editar])
async def sincronizar_publicacoes(
    db: Annotated[AsyncSession, Depends(get_db)],
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[PublicacaoRead]:
    try:
        novas = await publicacao_service.sincronizar(db, data_inicio=data_inicio, data_fim=data_fim)
    except DjenError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    # recarrega com relacionamento processo para a serialização
    return [await publicacao_service.get_by_id(db, p.id) for p in novas]


@router.patch("/{publicacao_id}", response_model=PublicacaoRead, dependencies=[_editar])
async def atualizar_status_publicacao(
    publicacao_id: uuid.UUID,
    data: PublicacaoStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PublicacaoRead:
    publicacao = await publicacao_service.get_by_id(db, publicacao_id)
    if publicacao is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicação não encontrada")
    return await publicacao_service.atualizar_status(db, publicacao, data.status, current_user.id)
