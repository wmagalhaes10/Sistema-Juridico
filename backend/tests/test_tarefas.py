from datetime import date, timedelta

from app.models.enums import ModuloSistema
from tests.conftest import restringir_permissao
from tests.test_processos import criar_cliente, criar_processo


async def test_criar_tarefa_sem_processo(client, funcionario_headers):
    response = await client.post(
        "/tarefas",
        json={"titulo": "Ligar para cliente", "data_vencimento": str(date.today())},
        headers=funcionario_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["titulo"] == "Ligar para cliente"
    assert body["status"] == "pendente"
    assert body["processo_id"] is None


async def test_criar_tarefa_com_processo_e_responsavel(client, funcionario_headers):
    me = await client.get("/auth/me", headers=funcionario_headers)
    responsavel_id = me.json()["id"]

    cliente_id = await criar_cliente(client, funcionario_headers)
    processo = (await criar_processo(client, funcionario_headers, cliente_id)).json()

    response = await client.post(
        "/tarefas",
        json={
            "titulo": "Revisar petição",
            "processo_id": processo["id"],
            "responsavel_id": responsavel_id,
            "data_vencimento": str(date.today() + timedelta(days=2)),
        },
        headers=funcionario_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["processo"]["numero_cnj"] == processo["numero_cnj"]
    assert body["responsavel"]["id"] == responsavel_id


async def test_listar_tarefas_ordena_sem_data_por_ultimo(client, funcionario_headers):
    await client.post("/tarefas", json={"titulo": "Sem prazo"}, headers=funcionario_headers)
    await client.post(
        "/tarefas", json={"titulo": "Com prazo", "data_vencimento": str(date.today())}, headers=funcionario_headers
    )

    response = await client.get("/tarefas", headers=funcionario_headers)

    assert response.status_code == 200
    titulos = [t["titulo"] for t in response.json()]
    assert titulos == ["Com prazo", "Sem prazo"]


async def test_marcar_tarefa_concluida(client, funcionario_headers):
    criada = await client.post("/tarefas", json={"titulo": "Enviar e-mail"}, headers=funcionario_headers)
    tarefa_id = criada.json()["id"]

    response = await client.patch(f"/tarefas/{tarefa_id}", json={"status": "concluida"}, headers=funcionario_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "concluida"


async def test_filtrar_tarefas_por_responsavel_e_status(client, funcionario_headers):
    me = await client.get("/auth/me", headers=funcionario_headers)
    responsavel_id = me.json()["id"]

    t1 = await client.post(
        "/tarefas", json={"titulo": "A", "responsavel_id": responsavel_id}, headers=funcionario_headers
    )
    await client.post("/tarefas", json={"titulo": "B"}, headers=funcionario_headers)
    await client.patch(f"/tarefas/{t1.json()['id']}", json={"status": "concluida"}, headers=funcionario_headers)

    por_responsavel = await client.get(
        "/tarefas", params={"responsavel_id": responsavel_id}, headers=funcionario_headers
    )
    assert len(por_responsavel.json()) == 1

    pendentes = await client.get("/tarefas", params={"status_tarefa": "pendente"}, headers=funcionario_headers)
    assert len(pendentes.json()) == 1
    assert pendentes.json()[0]["titulo"] == "B"


async def test_excluir_tarefa(client, funcionario_headers):
    criada = await client.post("/tarefas", json={"titulo": "Remover"}, headers=funcionario_headers)
    tarefa_id = criada.json()["id"]

    response = await client.delete(f"/tarefas/{tarefa_id}", headers=funcionario_headers)
    assert response.status_code == 204

    lista = await client.get("/tarefas", headers=funcionario_headers)
    assert lista.json() == []


async def test_funcionario_sem_permissao_de_editar_tarefas_e_bloqueado(client, funcionario_headers, session_maker):
    me = await client.get("/auth/me", headers=funcionario_headers)
    await restringir_permissao(session_maker, me.json()["id"], ModuloSistema.TAREFAS, pode_editar=False)

    response = await client.post("/tarefas", json={"titulo": "Bloqueada"}, headers=funcionario_headers)
    assert response.status_code == 403


async def test_lista_basica_de_usuarios_acessivel_a_qualquer_autenticado(client, funcionario_headers):
    response = await client.get("/users/basico", headers=funcionario_headers)

    assert response.status_code == 200
    assert any(u["nome"] == "Teste" for u in response.json())
    # não deve vazar dados sensíveis
    assert "permissoes" not in response.json()[0]
    assert "email" not in response.json()[0]


async def test_lista_basica_de_usuarios_requer_autenticacao(client):
    response = await client.get("/users/basico")
    assert response.status_code == 401
