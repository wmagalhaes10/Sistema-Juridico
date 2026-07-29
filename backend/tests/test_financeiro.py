from datetime import date, timedelta
from decimal import Decimal

from tests.test_processos import criar_cliente, criar_processo


async def test_contrato_fixo_parcela_unica(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)

    response = await client.post(
        "/contratos-honorarios",
        json={
            "cliente_id": cliente_id,
            "tipo": "fixo",
            "valor_contratado": "3000.00",
            "numero_parcelas": 1,
            "data_assinatura": str(date.today()),
        },
        headers=funcionario_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert len(body["parcelas"]) == 1
    assert body["parcelas"][0]["valor"] == "3000.00"
    assert body["parcelas"][0]["status"] == "pendente"


async def test_contrato_parcelado_gera_vencimentos_mensais_e_ajusta_arredondamento(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)

    response = await client.post(
        "/contratos-honorarios",
        json={
            "cliente_id": cliente_id,
            "tipo": "exito",
            "valor_contratado": "1000.00",
            "numero_parcelas": 3,
            "data_assinatura": "2026-01-15",
        },
        headers=funcionario_headers,
    )

    assert response.status_code == 201
    parcelas = response.json()["parcelas"]
    assert len(parcelas) == 3
    assert parcelas[0]["data_vencimento"] == "2026-02-15"
    assert parcelas[1]["data_vencimento"] == "2026-03-15"
    assert parcelas[2]["data_vencimento"] == "2026-04-15"
    # soma das parcelas bate exatamente com o valor contratado, mesmo com dízima
    soma = sum(Decimal(p["valor"]) for p in parcelas)
    assert soma == Decimal("1000.00")


async def test_valor_contratado_invalido_rejeitado(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)

    response = await client.post(
        "/contratos-honorarios",
        json={"cliente_id": cliente_id, "tipo": "fixo", "valor_contratado": "0", "numero_parcelas": 1},
        headers=funcionario_headers,
    )

    assert response.status_code == 422


async def test_registrar_pagamento_e_recibo(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)
    contrato = (
        await client.post(
            "/contratos-honorarios",
            json={"cliente_id": cliente_id, "tipo": "fixo", "valor_contratado": "500.00", "numero_parcelas": 1},
            headers=funcionario_headers,
        )
    ).json()
    parcela_id = contrato["parcelas"][0]["id"]

    # recibo antes do pagamento deve falhar
    sem_pagamento = await client.get(f"/parcelas/{parcela_id}/recibo", headers=funcionario_headers)
    assert sem_pagamento.status_code == 400

    pago = await client.post(f"/parcelas/{parcela_id}/pagamento", headers=funcionario_headers)
    assert pago.status_code == 200
    assert pago.json()["status"] == "pago"
    assert pago.json()["data_pagamento"] == str(date.today())

    recibo = await client.get(f"/parcelas/{parcela_id}/recibo", headers=funcionario_headers)
    assert recibo.status_code == 200
    assert recibo.headers["content-type"] == "application/pdf"
    assert recibo.content.startswith(b"%PDF")


async def test_parcela_atrasada_calculada_dinamicamente(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)
    contrato = (
        await client.post(
            "/contratos-honorarios",
            json={
                "cliente_id": cliente_id,
                "tipo": "fixo",
                "valor_contratado": "100.00",
                "numero_parcelas": 1,
                "data_assinatura": str(date.today() - timedelta(days=30)),
            },
            headers=funcionario_headers,
        )
    ).json()

    assert contrato["parcelas"][0]["status"] == "atrasado"


async def test_despesas_e_saldo_do_processo(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)
    processo = (await criar_processo(client, funcionario_headers, cliente_id)).json()

    contrato = (
        await client.post(
            "/contratos-honorarios",
            json={
                "cliente_id": cliente_id,
                "processo_id": processo["id"],
                "tipo": "fixo",
                "valor_contratado": "2000.00",
                "numero_parcelas": 1,
            },
            headers=funcionario_headers,
        )
    ).json()
    parcela_id = contrato["parcelas"][0]["id"]
    await client.post(f"/parcelas/{parcela_id}/pagamento", headers=funcionario_headers)

    await client.post(
        f"/processos/{processo['id']}/despesas",
        json={"tipo": "custas", "descricao": "Custas iniciais", "valor": "300.00", "data_despesa": str(date.today())},
        headers=funcionario_headers,
    )

    saldo = await client.get(f"/processos/{processo['id']}/saldo", headers=funcionario_headers)

    assert saldo.status_code == 200
    body = saldo.json()
    assert body["total_receitas"] == "2000.00"
    assert body["total_despesas"] == "300.00"
    assert body["saldo"] == "1700.00"


async def test_relatorio_receitas_filtra_por_periodo(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)
    contrato = (
        await client.post(
            "/contratos-honorarios",
            json={"cliente_id": cliente_id, "tipo": "fixo", "valor_contratado": "800.00", "numero_parcelas": 1},
            headers=funcionario_headers,
        )
    ).json()
    parcela_id = contrato["parcelas"][0]["id"]
    await client.post(f"/parcelas/{parcela_id}/pagamento", headers=funcionario_headers)

    dentro = await client.get(
        "/relatorios/receitas",
        params={"data_inicio": str(date.today()), "data_fim": str(date.today())},
        headers=funcionario_headers,
    )
    assert dentro.json()["total"] == "800.00"
    assert dentro.json()["quantidade_parcelas"] == 1

    fora = await client.get(
        "/relatorios/receitas",
        params={"data_inicio": str(date.today() - timedelta(days=10)), "data_fim": str(date.today() - timedelta(days=5))},
        headers=funcionario_headers,
    )
    assert fora.json()["total"] == "0.00"
    assert fora.json()["quantidade_parcelas"] == 0
