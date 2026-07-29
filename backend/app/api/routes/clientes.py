import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permissao
from app.core.database import get_db
from app.models.cliente import Cliente
from app.models.enums import ModuloSistema
from app.schemas.cliente import ClienteCreate, ClienteListResponse, ClienteRead, ClienteUpdate
from app.services import cliente_service

router = APIRouter(prefix="/clientes", tags=["clientes"])


async def _get_cliente_or_404(cliente_id: uuid.UUID, db: AsyncSession) -> Cliente:
    cliente = await cliente_service.get_by_id(db, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return cliente


@router.get(
    "",
    response_model=ClienteListResponse,
    dependencies=[Depends(require_permissao(ModuloSistema.CLIENTES, "visualizar"))],
)
async def list_clientes(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    busca: str | None = None,
) -> ClienteListResponse:
    items, total = await cliente_service.list_clientes(db, page=page, page_size=page_size, busca=busca)
    return ClienteListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/{cliente_id}",
    response_model=ClienteRead,
    dependencies=[Depends(require_permissao(ModuloSistema.CLIENTES, "visualizar"))],
)
async def get_cliente(cliente_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> Cliente:
    return await _get_cliente_or_404(cliente_id, db)


@router.post(
    "",
    response_model=ClienteRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissao(ModuloSistema.CLIENTES, "editar"))],
)
async def create_cliente(data: ClienteCreate, db: Annotated[AsyncSession, Depends(get_db)]) -> Cliente:
    existente = await cliente_service.get_by_cpf_cnpj(db, data.cpf_cnpj)
    if existente is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="CPF/CNPJ já cadastrado")
    try:
        return await cliente_service.create_cliente(db, data)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="CPF/CNPJ já cadastrado")


@router.put(
    "/{cliente_id}",
    response_model=ClienteRead,
    dependencies=[Depends(require_permissao(ModuloSistema.CLIENTES, "editar"))],
)
async def update_cliente(
    cliente_id: uuid.UUID,
    data: ClienteUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Cliente:
    cliente = await _get_cliente_or_404(cliente_id, db)
    return await cliente_service.update_cliente(db, cliente, data)


@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permissao(ModuloSistema.CLIENTES, "excluir"))],
)
async def delete_cliente(cliente_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    cliente = await _get_cliente_or_404(cliente_id, db)
    try:
        await cliente_service.delete_cliente(db, cliente)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cliente possui processos ou contratos vinculados e não pode ser excluído",
        )
