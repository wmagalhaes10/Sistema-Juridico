from fastapi import APIRouter

from app.api.routes import auth, clientes, financeiro, integracoes, prazos, processos, publicacoes, tarefas, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(clientes.router)
api_router.include_router(processos.router)
api_router.include_router(prazos.router)
api_router.include_router(financeiro.router)
api_router.include_router(integracoes.router)
api_router.include_router(tarefas.router)
api_router.include_router(publicacoes.router)
