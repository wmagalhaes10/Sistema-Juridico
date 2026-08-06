from datetime import date, timedelta

from tests.test_processos import CNJ_VALIDO, criar_cliente, criar_processo


async def criar_processo_completo(client, headers) -> dict:
    cliente_id = await criar_cliente(client, headers)
    response = await criar_processo(client, headers, cliente_id)
    return response.json()


async def criar_prazo(client, headers, processo_id, data_prazo, tipo="peremptorio", **extra):
    return await client.post(
        f"/processos/{processo_id}/prazos",
        json={"data_prazo": str(data_prazo), "tipo": tipo, "descricao": "Contestação", **extra},
        headers=headers,
    )


async def test_criar_prazo(client, funcionario_headers):
    processo = await criar_processo_completo(client, funcionario_headers)

    response = await criar_prazo(client, funcionario_headers, processo["id"], date.today() + timedelta(days=10))

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pendente"
    assert body["processo"]["numero_cnj"] == "00000013920248260100"


async def test_listar_prazos_do_processo(client, funcionario_headers):
    processo = await criar_processo_completo(client, funcionario_headers)
    await criar_prazo(client, funcionario_headers, processo["id"], date.today() + timedelta(days=5))
    await criar_prazo(client, funcionario_headers, processo["id"], date.today() + timedelta(days=15), tipo="recursal")

    response = await client.get(f"/processos/{processo['id']}/prazos", headers=funcionario_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2
    # ordenados por data
    assert response.json()[0]["tipo"] == "peremptorio"


async def test_marcar_prazo_cumprido(client, funcionario_headers):
    processo = await criar_processo_completo(client, funcionario_headers)
    prazo = (await criar_prazo(client, funcionario_headers, processo["id"], date.today())).json()

    response = await client.patch(
        f"/prazos/{prazo['id']}", json={"status": "cumprido"}, headers=funcionario_headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cumprido"


async def test_filtrar_prazos_por_periodo_e_status(client, funcionario_headers):
    processo = await criar_processo_completo(client, funcionario_headers)
    hoje = date.today()
    await criar_prazo(client, funcionario_headers, processo["id"], hoje + timedelta(days=2))
    await criar_prazo(client, funcionario_headers, processo["id"], hoje + timedelta(days=40))

    proximos = await client.get(
        "/prazos",
        params={"data_inicio": str(hoje), "data_fim": str(hoje + timedelta(days=7))},
        headers=funcionario_headers,
    )
    assert proximos.json()["total"] == 1

    pendentes = await client.get("/prazos", params={"status_prazo": "pendente"}, headers=funcionario_headers)
    assert pendentes.json()["total"] == 2


async def test_dashboard_semanal(client, funcionario_headers):
    processo = await criar_processo_completo(client, funcionario_headers)
    hoje = date.today()
    # prazo dentro da semana atual
    await criar_prazo(client, funcionario_headers, processo["id"], hoje)
    # prazo vencido (semana passada, ainda pendente)
    await criar_prazo(client, funcionario_headers, processo["id"], hoje - timedelta(days=10))

    response = await client.get("/prazos/dashboard", params={"visao": "semanal"}, headers=funcionario_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["vencidos"] == 1
    assert any(p["data_prazo"] == str(hoje) for p in body["prazos"])


async def test_dashboard_mensal(client, funcionario_headers):
    processo = await criar_processo_completo(client, funcionario_headers)
    hoje = date.today()
    await criar_prazo(client, funcionario_headers, processo["id"], hoje.replace(day=15))

    response = await client.get("/prazos/dashboard", params={"visao": "mensal"}, headers=funcionario_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["inicio"] == str(hoje.replace(day=1))
    assert len(body["prazos"]) == 1


async def test_excluir_prazo(client, funcionario_headers):
    processo = await criar_processo_completo(client, funcionario_headers)
    prazo = (await criar_prazo(client, funcionario_headers, processo["id"], date.today())).json()

    response = await client.delete(f"/prazos/{prazo['id']}", headers=funcionario_headers)
    assert response.status_code == 204

    busca = await client.get(f"/prazos/{prazo['id']}", headers=funcionario_headers)
    assert busca.status_code == 404
