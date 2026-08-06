from app.models.enums import ModuloSistema
from tests.conftest import criar_usuario


async def test_login_success(client, session_maker):
    await criar_usuario(session_maker, "admin@example.com", "senha123", super_admin=True)

    response = await client.post("/auth/login", data={"username": "admin@example.com", "password": "senha123"})

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


async def test_login_invalid_password(client, session_maker):
    await criar_usuario(session_maker, "admin@example.com", "senha123", super_admin=True)

    response = await client.post("/auth/login", data={"username": "admin@example.com", "password": "errada"})

    assert response.status_code == 401


async def test_me_requires_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401


async def test_me_returns_current_user_com_permissoes(client, session_maker):
    await criar_usuario(session_maker, "funcionario@example.com", "senha123")
    login = await client.post("/auth/login", data={"username": "funcionario@example.com", "password": "senha123"})
    token = login.json()["access_token"]

    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "funcionario@example.com"
    assert body["super_admin"] is False
    # nasce com acesso total: todos os módulos, com as três ações liberadas
    assert len(body["permissoes"]) == 6
    assert all(p["pode_visualizar"] and p["pode_editar"] and p["pode_excluir"] for p in body["permissoes"])


async def test_refresh_token_flow(client, session_maker):
    await criar_usuario(session_maker, "admin@example.com", "senha123", super_admin=True)
    login = await client.post("/auth/login", data={"username": "admin@example.com", "password": "senha123"})
    refresh_token = login.json()["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_create_user_requires_super_admin(client, session_maker):
    await criar_usuario(session_maker, "funcionario@example.com", "senha123")
    login = await client.post("/auth/login", data={"username": "funcionario@example.com", "password": "senha123"})
    token = login.json()["access_token"]

    response = await client.post(
        "/users",
        json={"nome": "Novo", "email": "novo@example.com", "password": "abc12345"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


async def test_create_user_as_super_admin_nasce_com_acesso_total(client, session_maker):
    await criar_usuario(session_maker, "admin@example.com", "senha123", super_admin=True)
    login = await client.post("/auth/login", data={"username": "admin@example.com", "password": "senha123"})
    token = login.json()["access_token"]

    response = await client.post(
        "/users",
        json={"nome": "Novo", "email": "novo@example.com", "password": "abc12345"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "novo@example.com"
    assert len(body["permissoes"]) == 6
    assert all(p["pode_visualizar"] and p["pode_editar"] and p["pode_excluir"] for p in body["permissoes"])


async def test_super_admin_pode_restringir_permissao_de_funcionario(client, session_maker):
    admin = await criar_usuario(session_maker, "admin@example.com", "senha123", super_admin=True)
    login = await client.post("/auth/login", data={"username": "admin@example.com", "password": "senha123"})
    token = login.json()["access_token"]

    criado = await client.post(
        "/users",
        json={"nome": "Novo", "email": "novo@example.com", "password": "abc12345"},
        headers={"Authorization": f"Bearer {token}"},
    )
    funcionario_id = criado.json()["id"]

    response = await client.patch(
        f"/users/{funcionario_id}/permissoes/{ModuloSistema.FINANCEIRO.value}",
        json={"pode_visualizar": False, "pode_editar": False, "pode_excluir": False},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["pode_visualizar"] is False

    # confirma refletido no GET /users/{id}
    get_response = await client.get(f"/users/{funcionario_id}", headers={"Authorization": f"Bearer {token}"})
    financeiro = next(p for p in get_response.json()["permissoes"] if p["modulo"] == "financeiro")
    assert financeiro["pode_visualizar"] is False
    assert admin.super_admin is True  # sanity check do fixture


async def test_nao_ha_permissoes_configuraveis_para_super_admin(client, session_maker):
    await criar_usuario(session_maker, "admin@example.com", "senha123", super_admin=True)
    login = await client.post("/auth/login", data={"username": "admin@example.com", "password": "senha123"})
    token = login.json()["access_token"]

    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    admin_id = me.json()["id"]

    response = await client.patch(
        f"/users/{admin_id}/permissoes/{ModuloSistema.CLIENTES.value}",
        json={"pode_visualizar": False},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
