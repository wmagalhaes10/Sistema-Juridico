import httpx

from app.core.config import settings

DATAJUD_BASE_URL = "https://api-publica.datajud.cnj.jus.br"


class DataJudError(Exception):
    pass


def _endpoint(tribunal: str) -> str:
    """Monta a URL do alias público do tribunal (ex.: TJSP -> api_publica_tjsp)."""
    alias = tribunal.strip().lower()
    return f"{DATAJUD_BASE_URL}/api_publica_{alias}/_search"


async def consultar_processo(
    numero_cnj: str,
    tribunal: str,
    client: httpx.AsyncClient | None = None,
) -> dict:
    if not settings.DATAJUD_API_KEY:
        raise DataJudError("DATAJUD_API_KEY não configurada")
    if not tribunal:
        raise DataJudError("Processo sem tribunal cadastrado")

    fechar_cliente = client is None
    client = client or httpx.AsyncClient(timeout=15)
    try:
        response = await client.post(
            _endpoint(tribunal),
            headers={
                "Authorization": f"APIKey {settings.DATAJUD_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"query": {"match": {"numeroProcesso": numero_cnj}}},
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPError as exc:
        raise DataJudError(f"Falha ao consultar DataJud: {exc}") from exc
    finally:
        if fechar_cliente:
            await client.aclose()

    hits = payload.get("hits", {}).get("hits", [])
    if not hits:
        return {}
    return hits[0].get("_source", {})
