from datetime import date

import httpx
import pytest

from app.services import datajud_service, feriado_service, sincronizacao_service
from app.services.datajud_service import DataJudError
from tests.test_processos import criar_cliente, criar_processo


def _mock_transport(handler):
    return httpx.MockTransport(handler)


def _feriados_2026_handler(request: httpx.Request) -> httpx.Response:
    assert request.url.path.endswith("/2026")
    return httpx.Response(
        200,
        json=[
            {"date": "2026-01-01", "name": "Confraternização Universal", "type": "national"},
            {"date": "2026-04-21", "name": "Tiradentes", "type": "national"},
        ],
    )


async def test_sincronizar_feriados_e_idempotencia(session_maker):
    async with session_maker() as db:
        client = httpx.AsyncClient(transport=_mock_transport(_feriados_2026_handler))
        criados = await feriado_service.sincronizar_feriados(db, 2026, client=client)
        await client.aclose()
        assert len(criados) == 2

        client2 = httpx.AsyncClient(transport=_mock_transport(_feriados_2026_handler))
        criados_novamente = await feriado_service.sincronizar_feriados(db, 2026, client=client2)
        await client2.aclose()
        assert len(criados_novamente) == 0

        todos = await feriado_service.list_feriados(db, ano=2026)
        assert len(todos) == 2


async def test_dia_util_considera_fim_de_semana_e_feriado(session_maker):
    async with session_maker() as db:
        client = httpx.AsyncClient(transport=_mock_transport(_feriados_2026_handler))
        await feriado_service.sincronizar_feriados(db, 2026, client=client)
        await client.aclose()

        assert await feriado_service.is_dia_util(db, date(2026, 1, 1)) is False  # feriado
        assert await feriado_service.is_dia_util(db, date(2026, 1, 3)) is False  # sábado
        assert await feriado_service.is_dia_util(db, date(2026, 1, 5)) is True  # segunda comum


async def test_adicionar_dias_uteis_pula_feriado_e_fim_de_semana(session_maker):
    async with session_maker() as db:
        client = httpx.AsyncClient(transport=_mock_transport(_feriados_2026_handler))
        await feriado_service.sincronizar_feriados(db, 2026, client=client)
        await client.aclose()

        # a partir de 30/12/2025 (terça), +2 dias úteis:
        # 31/dez (qua) conta 1, 01/jan é feriado (não conta), 02/jan (sex) conta 2
        resultado = await feriado_service.adicionar_dias_uteis(db, date(2025, 12, 30), 2)
        assert resultado == date(2026, 1, 2)


async def test_datajud_sem_api_key_lanca_erro(session_maker, monkeypatch):
    monkeypatch.setattr("app.services.datajud_service.settings.DATAJUD_API_KEY", "")
    with pytest.raises(DataJudError):
        await datajud_service.consultar_processo("00000013920248260100", "TJSP")


async def test_datajud_monta_endpoint_e_parseia_resposta(monkeypatch):
    monkeypatch.setattr("app.services.datajud_service.settings.DATAJUD_API_KEY", "chave-teste")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api_publica_tjsp/_search"
        assert request.headers["authorization"] == "APIKey chave-teste"
        return httpx.Response(
            200,
            json={
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "numeroProcesso": "00000013920248260100",
                                "movimentos": [
                                    {"nome": "Distribuição", "dataHora": "2024-01-10T10:00:00.000Z"},
                                ],
                            }
                        }
                    ]
                }
            },
        )

    client = httpx.AsyncClient(transport=_mock_transport(handler))
    dados = await datajud_service.consultar_processo("00000013920248260100", "TJSP", client=client)
    await client.aclose()

    assert dados["numeroProcesso"] == "00000013920248260100"
    assert len(dados["movimentos"]) == 1


async def test_datajud_sem_resultado_retorna_vazio(monkeypatch):
    monkeypatch.setattr("app.services.datajud_service.settings.DATAJUD_API_KEY", "chave-teste")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"hits": {"hits": []}})

    client = httpx.AsyncClient(transport=_mock_transport(handler))
    dados = await datajud_service.consultar_processo("00000013920248260100", "TJSP", client=client)
    await client.aclose()

    assert dados == {}


async def test_sincronizacao_cria_movimentacoes_e_prazo_automatico(client, funcionario_headers, session_maker, monkeypatch):
    monkeypatch.setattr("app.services.datajud_service.settings.DATAJUD_API_KEY", "chave-teste")

    cliente_id = await criar_cliente(client, funcionario_headers)
    processo_resp = await criar_processo(client, funcionario_headers, cliente_id)
    processo_id = processo_resp.json()["id"]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "movimentos": [
                                    {"nome": "Juntada de petição", "dataHora": "2026-06-01T09:00:00.000Z"},
                                    {
                                        "nome": "Intimação para manifestação",
                                        "dataHora": "2026-06-02T09:00:00.000Z",
                                    },
                                ]
                            }
                        }
                    ]
                }
            },
        )

    mock_client = httpx.AsyncClient(transport=_mock_transport(handler))

    async with session_maker() as db:
        from app.services import processo_service, sincronizacao_service
        import uuid as uuid_mod

        processo = await processo_service.get_by_id(db, uuid_mod.UUID(processo_id))
        novas = await sincronizacao_service.sincronizar_processo(db, processo, client=mock_client)

    await mock_client.aclose()

    assert len(novas) == 2

    movimentacoes = await client.get(f"/processos/{processo_id}/movimentacoes", headers=funcionario_headers)
    assert movimentacoes.status_code == 200
    assert len(movimentacoes.json()) == 2
    assert all(m["origem"] == "datajud" for m in movimentacoes.json())

    # a movimentação de "intimação" deve ter gerado um prazo automático
    prazos = await client.get(f"/processos/{processo_id}/prazos", headers=funcionario_headers)
    assert prazos.status_code == 200
    assert len(prazos.json()) == 1
    assert "Intimação" in prazos.json()[0]["descricao"]


async def test_sincronizacao_e_idempotente(session_maker, client, funcionario_headers, monkeypatch):
    monkeypatch.setattr("app.services.datajud_service.settings.DATAJUD_API_KEY", "chave-teste")

    cliente_id = await criar_cliente(client, funcionario_headers)
    processo_resp = await criar_processo(client, funcionario_headers, cliente_id)
    processo_id = processo_resp.json()["id"]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "hits": {
                    "hits": [
                        {"_source": {"movimentos": [{"nome": "Despacho", "dataHora": "2026-06-01T09:00:00.000Z"}]}}
                    ]
                }
            },
        )

    async with session_maker() as db:
        from app.services import processo_service, sincronizacao_service
        import uuid as uuid_mod

        processo = await processo_service.get_by_id(db, uuid_mod.UUID(processo_id))

        c1 = httpx.AsyncClient(transport=_mock_transport(handler))
        primeira = await sincronizacao_service.sincronizar_processo(db, processo, client=c1)
        await c1.aclose()

        c2 = httpx.AsyncClient(transport=_mock_transport(handler))
        segunda = await sincronizacao_service.sincronizar_processo(db, processo, client=c2)
        await c2.aclose()

    assert len(primeira) == 1
    assert len(segunda) == 0  # já existia, não duplicou
