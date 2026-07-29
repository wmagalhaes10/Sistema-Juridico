import argparse
import asyncio

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.services.user_service import get_by_email


async def create_admin(nome: str, email: str, password: str) -> None:
    async with AsyncSessionLocal() as session:
        existing = await get_by_email(session, email)
        if existing is not None:
            print(f"Usuário {email} já existe.")
            return

        user = User(
            nome=nome,
            email=email,
            hashed_password=hash_password(password),
            super_admin=True,
        )
        session.add(user)
        await session.commit()
        print(f"Admin {email} criado com sucesso (acesso total e irrestrito).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria o primeiro usuário admin do sistema.")
    parser.add_argument("--nome", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    asyncio.run(create_admin(args.nome, args.email, args.password))


if __name__ == "__main__":
    main()
