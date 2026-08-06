CLIENTE = {
    "tipo_pessoa": "fisica",
    "cpf_cnpj": "529.982.247-25",
    "nome_razao_social": "João da Silva",
}

# números CNJ com dígito verificador válido (ISO 7064 mod 97-10)
CNJ_VALIDO = "0000001-39.2024.8.26.0100"
CNJ_VALIDO_2 = "0001234-52.2023.8.26.0053"


async def criar_cliente(client, headers) -> str:
    response = await client.post("/clientes", json=CLIENTE, headers=headers)
    return response.json()["id"]


async def criar_processo(client, headers, cliente_id, numero=CNJ_VALIDO) -> dict:
    response = await client.post(
        "/processos",
        json={
            "numero_cnj": numero,
            "cliente_id": cliente_id,
            "vara": "2ª Vara Cível",
            "tribunal": "TJSP",
            "comarca": "São Paulo",
            "tipo_acao": "Ação de Cobrança",
            "polo_ativo": "João da Silva",
            "polo_passivo": "Empresa XYZ Ltda",
        },
        headers=headers,
    )
    return response


async def test_criar_processo(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)

    response = await criar_processo(client, funcionario_headers, cliente_id)

    assert response.status_code == 201
    body = response.json()
    assert body["numero_cnj"] == "00000013920248260100"  # normalizado
    assert body["cliente"]["nome_razao_social"] == "João da Silva"
    assert body["fase_processual"] == "conhecimento"
    assert body["status"] == "ativo"


async def test_numero_cnj_invalido_rejeitado(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)

    response = await criar_processo(client, funcionario_headers, cliente_id, numero="0000001-00.2024.8.26.0100")

    assert response.status_code == 422


async def test_processo_duplicado(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)
    await criar_processo(client, funcionario_headers, cliente_id)

    response = await criar_processo(client, funcionario_headers, cliente_id)

    assert response.status_code == 409


async def test_processo_cliente_inexistente(client, funcionario_headers):
    response = await criar_processo(
        client, funcionario_headers, "00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 422


async def test_listar_processos_com_filtros(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)
    await criar_processo(client, funcionario_headers, cliente_id)
    await criar_processo(client, funcionario_headers, cliente_id, numero=CNJ_VALIDO_2)

    todos = await client.get("/processos", headers=funcionario_headers)
    assert todos.json()["total"] == 2

    por_cliente = await client.get("/processos", params={"cliente_id": cliente_id}, headers=funcionario_headers)
    assert por_cliente.json()["total"] == 2

    busca = await client.get("/processos", params={"busca": "0001234"}, headers=funcionario_headers)
    assert busca.json()["total"] == 1


async def test_atualizar_fase_e_status(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)
    processo = (await criar_processo(client, funcionario_headers, cliente_id)).json()

    response = await client.put(
        f"/processos/{processo['id']}",
        json={"fase_processual": "recursal", "status": "suspenso"},
        headers=funcionario_headers,
    )

    assert response.status_code == 200
    assert response.json()["fase_processual"] == "recursal"
    assert response.json()["status"] == "suspenso"


async def test_movimentacoes(client, funcionario_headers):
    cliente_id = await criar_cliente(client, funcionario_headers)
    processo = (await criar_processo(client, funcionario_headers, cliente_id)).json()

    criada = await client.post(
        f"/processos/{processo['id']}/movimentacoes",
        json={"data_movimentacao": "2026-07-10T14:30:00", "descricao": "Juntada de petição"},
        headers=funcionario_headers,
    )
    assert criada.status_code == 201
    assert criada.json()["origem"] == "manual"

    lista = await client.get(f"/processos/{processo['id']}/movimentacoes", headers=funcionario_headers)
    assert lista.status_code == 200
    assert len(lista.json()) == 1
