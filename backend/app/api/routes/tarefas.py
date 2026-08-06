import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permissao
from app.core.database import get_db
from app.models.enums import ModuloSistema, StatusTarefa
from app.models.user import User
from app.schemas.tarefa import TarefaCreate, TarefaRead, TarefaUpdate
from app.services import tarefa_service

router = APIRouter(prefix="/tarefas", tags=["tarefas"])


async def _get_tarefa_or_404(tarefa_id: uuid.UUID, db: AsyncSession):
    tarefa = await tarefa_service.get_by_id(db, tarefa_id)
    if tarefa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    return tarefa


@router.get(
    "",
    response_model=list[TarefaRead],
    dependencies=[Depends(require_permissao(ModuloSistema.TAREFAS, "visualizar"))],
)
async def list_tarefas(
    db: Annotated[AsyncSession, Depends(get_db)],
    responsavel_id: uuid.UUID | None = None,
    status_tarefa: StatusTarefa | None = None,
    processo_id: uuid.UUID | None = None,
) -> list[TarefaRead]:
    return await tarefa_service.list_tarefas(
        db, responsavel_id=responsavel_id, status=status_tarefa, processo_id=processo_id
    )


@router.post(
    "",
    response_model=TarefaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissao(ModuloSistema.TAREFAS, "editar"))],
)
async def create_tarefa(
    data: TarefaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TarefaRead:
    return await tarefa_service.create_tarefa(db, data, criado_por_id=current_user.id)


@router.patch(
    "/{tarefa_id}",
    response_model=TarefaRead,
    dependencies=[Depends(require_permissao(ModuloSistema.TAREFAS, "editar"))],
)
async def update_tarefa(
    tarefa_id: uuid.UUID,
    data: TarefaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TarefaRead:
    tarefa = await _get_tarefa_or_404(tarefa_id, db)
    return await tarefa_service.update_tarefa(db, tarefa, data)


@router.delete(
    "/{tarefa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permissao(ModuloSistema.TAREFAS, "excluir"))],
)
async def delete_tarefa(tarefa_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> None:
    tarefa = await _get_tarefa_or_404(tarefa_id, db)
    await tarefa_service.delete_tarefa(db, tarefa)
