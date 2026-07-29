CLIENTE_PF = {
    "tipo_pessoa": "fisica",
    "cpf_cnpj": "529.982.247-25",
    "nome_razao_social": "João da Silva",
    "telefone": "(11) 99999-0000",
    "email": "joao@example.com",
}

CLIENTE_PJ = {
    "tipo_pessoa": "juridica",
    "cpf_cnpj": "11.222.333/0001-81",
    "nome_razao_social": "Empresa Exemplo Ltda",
}


async def test_criar_cliente_pf(client, funcionario_headers):
    response = await client.post("/clientes", json=CLIENTE_PF, headers=funcionario_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["cpf_cnpj"] == "52998224725"  # normalizado, sem máscara
    assert body["nome_razao_social"] == "João da Silva"


async def test_criar_cliente_pj(client, funcionario_headers):
    response = await client.post("/clientes", json=CLIENTE_PJ, headers=funcionario_headers)

    assert response.status_code == 201
    assert response.json()["cpf_cnpj"] == "11222333000181"


async def test_cpf_invalido_rejeitado(client, funcionario_headers):
    payload = {**CLIENTE_PF, "cpf_cnpj": "111.111.111-11"}
    response = await client.post("/clientes", json=payload, headers=funcionario_headers)
    assert response.status_code == 422


async def test_cnpj_invalido_rejeitado(client, funcionario_headers):
    payload = {**CLIENTE_PJ, "cpf_cnpj": "11.222.333/0001-99"}
    response = await client.post("/clientes", json=payload, headers=funcionario_headers)
    assert response.status_code == 422


async def test_cpf_cnpj_duplicado(client, funcionario_headers):
    await client.post("/clientes", json=CLIENTE_PF, headers=funcionario_headers)
    response = await client.post("/clientes", json=CLIENTE_PF, headers=funcionario_headers)
    assert response.status_code == 409


async def test_listar_com_busca_e_paginacao(client, funcionario_headers):
    await client.post("/clientes", json=CLIENTE_PF, headers=funcionario_headers)
    await client.post("/clientes", json=CLIENTE_PJ, headers=funcionario_headers)

    todos = await client.get("/clientes", headers=funcionario_headers)
    assert todos.status_code == 200
    assert todos.json()["total"] == 2

    busca = await client.get("/clientes", params={"busca": "joão"}, headers=funcionario_headers)
    assert busca.json()["total"] == 1
    assert busca.json()["items"][0]["nome_razao_social"] == "João da Silva"

    paginado = await client.get("/clientes", params={"page_size": 1, "page": 2}, headers=funcionario_headers)
    assert paginado.json()["total"] == 2
    assert len(paginado.json()["items"]) == 1


async def test_atualizar_cliente(client, funcionario_headers):
    criado = await client.post("/clientes", json=CLIENTE_PF, headers=funcionario_headers)
    cliente_id = criado.json()["id"]

    response = await client.put(
        f"/clientes/{cliente_id}", json={"telefone": "(11) 98888-7777"}, headers=funcionario_headers
    )

    assert response.status_code == 200
    assert response.json()["telefone"] == "(11) 98888-7777"
    assert response.json()["nome_razao_social"] == "João da Silva"


async def test_excluir_cliente_como_advogado(client, funcionario_headers):
    criado = await client.post("/clientes", json=CLIENTE_PF, headers=funcionario_headers)
    cliente_id = criado.json()["id"]

    response = await client.delete(f"/clientes/{cliente_id}", headers=funcionario_headers)
    assert response.status_code == 204

    busca = await client.get(f"/clientes/{cliente_id}", headers=funcionario_headers)
    assert busca.status_code == 404


async def test_funcionario_sem_permissao_de_excluir_e_bloqueado(client, funcionario_headers, session_maker):
    from app.models.enums import ModuloSistema
    from tests.conftest import restringir_permissao

    me = await client.get("/auth/me", headers=funcionario_headers)
    await restringir_permissao(session_maker, me.json()["id"], ModuloSistema.CLIENTES, pode_excluir=False)

    criado = await client.post("/clientes", json=CLIENTE_PF, headers=funcionario_headers)
    cliente_id = criado.json()["id"]

    response = await client.delete(f"/clientes/{cliente_id}", headers=funcionario_headers)
    assert response.status_code == 403


async def test_funcionario_sem_permissao_de_visualizar_e_bloqueado(client, funcionario_headers, session_maker):
    from app.models.enums import ModuloSistema
    from tests.conftest import restringir_permissao

    me = await client.get("/auth/me", headers=funcionario_headers)
    await restringir_permissao(session_maker, me.json()["id"], ModuloSistema.CLIENTES, pode_visualizar=False)

    response = await client.get("/clientes", headers=funcionario_headers)
    assert response.status_code == 403


async def test_rotas_exigem_autenticacao(client):
    response = await client.get("/clientes")
    assert response.status_code == 401
