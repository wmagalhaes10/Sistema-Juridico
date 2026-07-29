from datetime import date

import httpx
import pytest

from app.models.enums import ModuloSistema
from app.services import publicacao_service
from app.services.djen_service import DjenError, oabs_configuradas
from tests.conftest import restringir_permissao
from tests.test_processos import criar_cliente, criar_processo

COMUNICACAO_BASE = {
    "id": 677726704,
    "data_disponibilizacao": "2026-07-24",
    "siglaTribunal": "TRT1",
    "tipoComunicacao": "Intimação",
    "tipoDocumento": "Acórdão",
    "nomeOrgao": "9ª Turma",
    "nomeClasse": "RECURSO ORDINÁRIO TRABALHISTA",
    "numero_processo": "01007011920255010008",
    "texto": "PODER JUDICIÁRIO... intimação para ciência do acórdão.",
    "link": "https://pje.trt1.jus.br/validacao/xyz",
    "meio": "D",
    "meiocompleto": "Diário de Justiça Eletrônico Nacional",
}


def _mock_djen(itens_por_pagina_respostas: list[list[dict]]):
    """Handler que devolve páginas sucessivas; count = total de itens somados."""
    total = sum(len(p) for p in itens_por_pagina_respostas)
    chamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        pagina = int(request.url.params.get("pagina", "1"))
        chamadas.append(dict(request.url.params))
        itens = itens_por_pagina_respostas[pagina - 1] if pagina <= len(itens_por_pagina_respostas) else []
        return httpx.Response(200, json={"status": "success", "count": total, "items": itens})

    return handler, chamadas


async def test_oabs_configuradas_parse(monkeypatch):
    monkeypatch.setattr("app.services.djen_service.settings.DJEN_OABS", "240608/RJ, 111222/SP")
    assert oabs_configuradas() == [("240608", "RJ"), ("111222", "SP")]


async def test_oabs_mal_formatada_lanca_erro(monkeypatch):
    monkeypatch.setattr("app.services.djen_service.settings.DJEN_OABS", "240608RJ")
    with pytest.raises(DjenError):
        oabs_configuradas()


async def test_sincronizar_importa_e_e_idempotente(session_maker, monkeypatch):
    monkeypatch.setattr("app.services.djen_service.settings.DJEN_OABS", "240608/RJ")
    handler, chamadas = _mock_djen([[COMUNICACAO_BASE]])

    async with session_maker() as db:
        c1 = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        novas = await publicacao_service.sincronizar(db, client=c1)
        await c1.aclose()
        assert len(novas) == 1
        assert novas[0].sigla_tribunal == "TRT1"
        assert novas[0].oab_numero == "240608"
        assert chamadas[0]["numeroOab"] == "240608"
        assert chamadas[0]["ufOab"] == "RJ"

        c2 = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        repetidas = await publicacao_service.sincronizar(db, client=c2)
        await c2.aclose()
        assert repetidas == []


async def test_sincronizar_pagina_ate_o_fim(session_maker, monkeypatch):
    monkeypatch.setattr("app.services.djen_service.settings.DJEN_OABS", "240608/RJ")
    pagina1 = [{**COMUNICACAO_BASE, "id": 1}, {**COMUNICACAO_BASE, "id": 2}]
    pagina2 = [{**COMUNICACAO_BASE, "id": 3}]
    handler, chamadas = _mock_djen([pagina1, pagina2])

    async with session_maker() as db:
        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        novas = await publicacao_service.sincronizar(db, client=client)
        await client.aclose()

    assert len(novas) == 3
    assert len(chamadas) == 2  # duas páginas consultadas


async def test_sincronizar_vincula_processo_existente(client, funcionario_headers, session_maker, monkeypatch):
    monkeypatch.setattr("app.services.djen_service.settings.DJEN_OABS", "240608/RJ")

    cliente_id = await criar_cliente(client, funcionario_headers)
    processo_resp = await criar_processo(client, funcionario_headers, cliente_id)
    numero_cnj = processo_resp.json()["numero_cnj"]

    comunicacao = {**COMUNICACAO_BASE, "numero_processo": numero_cnj}
    handler, _ = _mock_djen([[comunicacao]])

    async with session_maker() as db:
        mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        novas = await publicacao_service.sincronizar(db, client=mock_client)
        await mock_client.aclose()

    assert novas[0].processo_id is not None

    lista = await client.get("/publicacoes", headers=funcionario_headers)
    assert lista.status_code == 200
    assert lista.json()["items"][0]["processo"]["numero_cnj"] == numero_cnj


async def test_tratar_e_descartar_publicacao(client, funcionario_headers, session_maker, monkeypatch):
    monkeypatch.setattr("app.services.djen_service.settings.DJEN_OABS", "240608/RJ")
    handler, _ = _mock_djen([[COMUNICACAO_BASE]])

    async with session_maker() as db:
        mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        await publicacao_service.sincronizar(db, client=mock_client)
        await mock_client.aclose()

    lista = await client.get("/publicacoes", headers=funcionario_headers)
    publicacao_id = lista.json()["items"][0]["id"]
    assert lista.json()["items"][0]["status"] == "nao_tratada"

    tratada = await client.patch(
        f"/publicacoes/{publicacao_id}", json={"status": "tratada"}, headers=funcionario_headers
    )
    assert tratada.status_code == 200
    assert tratada.json()["status"] == "tratada"

    resumo = await client.get("/publicacoes/resumo", headers=funcionario_headers)
    assert resumo.json()["tratadas"] == 1
    assert resumo.json()["nao_tratadas"] == 0


async def test_filtro_por_status(client, funcionario_headers, session_maker, monkeypatch):
    monkeypatch.setattr("app.services.djen_service.settings.DJEN_OABS", "240608/RJ")
    handler, _ = _mock_djen([[{**COMUNICACAO_BASE, "id": 10}, {**COMUNICACAO_BASE, "id": 11}]])

    async with session_maker() as db:
        mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        await publicacao_service.sincronizar(db, client=mock_client)
        await mock_client.aclose()

    lista = await client.get("/publicacoes", headers=funcionario_headers)
    primeiro_id = lista.json()["items"][0]["id"]
    await client.patch(f"/publicacoes/{primeiro_id}", json={"status": "descartada"}, headers=funcionario_headers)

    nao_tratadas = await client.get(
        "/publicacoes", params={"status_publicacao": "nao_tratada"}, headers=funcionario_headers
    )
    assert nao_tratadas.json()["total"] == 1

    descartadas = await client.get(
        "/publicacoes", params={"status_publicacao": "descartada"}, headers=funcionario_headers
    )
    assert descartadas.json()["total"] == 1


async def test_funcionario_sem_permissao_e_bloqueado(client, funcionario_headers, session_maker):
    me = await client.get("/auth/me", headers=funcionario_headers)
    await restringir_permissao(
        session_maker, me.json()["id"], ModuloSistema.PUBLICACOES, pode_visualizar=False
    )

    response = await client.get("/publicacoes", headers=funcionario_headers)
    assert response.status_code == 403


async def test_data_invalida_nao_quebra_sincronizacao(session_maker, monkeypatch):
    monkeypatch.setattr("app.services.djen_service.settings.DJEN_OABS", "240608/RJ")
    sem_data = {**COMUNICACAO_BASE, "id": 99, "data_disponibilizacao": None}
    handler, _ = _mock_djen([[sem_data]])

    async with session_maker() as db:
        mock_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        novas = await publicacao_service.sincronizar(db, client=mock_client)
        await mock_client.aclose()

    assert len(novas) == 1
    assert novas[0].data_disponibilizacao == date.today()
