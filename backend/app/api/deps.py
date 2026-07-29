import uuid
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.enums import ModuloSistema
from app.models.user import User
from app.services import permissao_service, user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não foi possível validar as credenciais",
    headers={"WWW-Authenticate": "Bearer"},
)

Acao = Literal["visualizar", "editar", "excluir"]

_CAMPO_POR_ACAO: dict[Acao, str] = {
    "visualizar": "pode_visualizar",
    "editar": "pode_editar",
    "excluir": "pode_excluir",
}


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = decode_token(token)
    except JWTError:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception

    user = await user_service.get_by_id(db, uuid.UUID(sub))
    if user is None or not user.ativo:
        raise credentials_exception

    return user


def require_super_admin():
    async def checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if not current_user.super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o administrador pode executar esta ação",
            )
        return current_user

    return checker


def require_permissao(modulo: ModuloSistema, acao: Acao):
    async def checker(
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> User:
        if current_user.super_admin:
            return current_user

        permissao = await permissao_service.get(db, current_user.id, modulo)
        if permissao is None or not getattr(permissao, _CAMPO_POR_ACAO[acao]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para executar esta ação",
            )
        return current_user

    return checker
