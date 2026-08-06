import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_super_admin
from app.core.database import get_db
from app.models.enums import ModuloSistema
from app.schemas.permissao import PermissaoRead, PermissaoUpdate
from app.schemas.user import UserCreate, UserRead, UserUpdate, UsuarioBasico
from app.services import permissao_service, user_service

router = APIRouter(prefix="/users", tags=["users"])


async def _get_user_or_404(user_id: uuid.UUID, db: AsyncSession):
    user = await user_service.get_by_id_com_permissoes(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user


@router.get("/basico", response_model=list[UsuarioBasico], dependencies=[Depends(get_current_user)])
async def list_usuarios_basico(db: Annotated[AsyncSession, Depends(get_db)]) -> list[UsuarioBasico]:
    """Lista enxuta de usuários ativos, para seletores de responsável (ex.: prazos e tarefas).
    Qualquer usuário autenticado pode consultar — não expõe permissões nem dados sensíveis."""
    return await user_service.list_ativos_basico(db)


@router.get("", response_model=list[UserRead], dependencies=[Depends(require_super_admin())])
async def list_users(db: Annotated[AsyncSession, Depends(get_db)]) -> list[UserRead]:
    return await user_service.list_funcionarios(db)


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_super_admin())])
async def get_user(user_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> UserRead:
    return await _get_user_or_404(user_id, db)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_super_admin())])
async def create_user(data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]) -> UserRead:
    existing = await user_service.get_by_email(db, data.email)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")
    return await user_service.create_user(db, data)


@router.put("/{user_id}", response_model=UserRead, dependencies=[Depends(require_super_admin())])
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    user = await _get_user_or_404(user_id, db)
    return await user_service.update_user(db, user, data)


@router.patch(
    "/{user_id}/permissoes/{modulo}",
    response_model=PermissaoRead,
    dependencies=[Depends(require_super_admin())],
)
async def update_permissao(
    user_id: uuid.UUID,
    modulo: ModuloSistema,
    data: PermissaoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PermissaoRead:
    user = await _get_user_or_404(user_id, db)
    if user.super_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O administrador sempre tem acesso total; não há permissões para configurar",
        )

    permissao = await permissao_service.get(db, user_id, modulo)
    if permissao is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permissão não encontrada")
    return await permissao_service.update(db, permissao, data)
