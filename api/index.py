import sys
from pathlib import Path

# O código do backend fica em backend/ — adiciona ao path para importar "app"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app  # noqa: E402


@app.middleware("http")
async def _debug_path(request, call_next):
    response = await call_next(request)
    response.headers["X-Orig-Path"] = request.url.path
    response.headers["X-Root-Path"] = request.scope.get("root_path", "")
    return response
