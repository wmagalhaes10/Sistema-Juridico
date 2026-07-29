import sys
from pathlib import Path

# O código do backend fica em backend/ — adiciona ao path para importar "app"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import app  # noqa: E402,F401
