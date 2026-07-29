from datetime import date

import httpx

from app.core.config import settings


class DjenError(Exception):
    pass


def oabs_configuradas() -> list[tuple[str, str]]:
    """Lê DJEN_OABS ("123456/RJ,654321/SP") e devolve [(numero, uf), ...]."""
    resultado: list[tuple[str, str]] = []
    for entrada in settings.DJEN_OABS.split(","):
        entrada = entrada.strip()
        if not entrada:
            continue
        try:
            numero, uf = entrada.split("/")
        except ValueError:
            raise DjenError(f"DJEN_OABS mal formatada: '{entrada}' (esperado numero/UF)")
        resultado.append((numero.strip(), uf.strip().upper()))
    return resultado


async def consultar_comunicacoes(
    numero_oab: str,
    uf_oab: str,
    data_inicio: date,
    data_fim: date,
    client: httpx.AsyncClient | None = None,
    itens_por_pagina: int = 100,
) -> list[dict]:
    """Busca todas as comunicações da OAB no período, paginando até o fim."""
    fechar_cliente = client is None
    client = client or httpx.AsyncClient(timeout=30)

    comunicacoes: list[dict] = []
    pagina = 1
    try:
        while True:
            response = await client.get(
                f"{settings.DJEN_BASE_URL}/comunicacao",
                params={
                    "numeroOab": numero_oab,
                    "ufOab": uf_oab,
                    "dataDisponibilizacaoInicio": data_inicio.isoformat(),
                    "dataDisponibilizacaoFim": data_fim.isoformat(),
                    "itensPorPagina": itens_por_pagina,
                    "pagina": pagina,
                },
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()

            itens = payload.get("items", [])
            comunicacoes.extend(itens)

            total = payload.get("count", 0)
            if len(comunicacoes) >= total or not itens:
                break
            pagina += 1
    except httpx.HTTPError as exc:
        raise DjenError(f"Falha ao consultar o DJEN: {exc}") from exc
    finally:
        if fechar_cliente:
            await client.aclose()

    return comunicacoes
