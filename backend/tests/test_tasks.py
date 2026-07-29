from datetime import date, timedelta

from app.services.datajud_service import DataJudError
from app.tasks import alertas, sincronizacao
from tests.test_processos import CNJ_VALIDO_2, criar_cliente, criar_processo


async def test_alerta_enviado_apenas_para_prazos_na_antecedencia_configurada(
    client, funcionario_headers, session_maker, monkeypatch
):
    monkeypatch.setattr("app.tasks.alertas.AsyncSessionLocal", session_maker)

    emails_enviados = []

    def fake_enviar_email(destinatario, assunto, corpo_html):
        emails_enviados.append((destinatario, assunto))

    monkeypatch.setattr("app.tasks.alertas.enviar_email", fake_enviar_email)

    me = await client.get("/auth/me", headers=funcionario_headers)
    responsavel_id = me.json()["id"]

    cliente_id = await criar_cliente(client, funcionario_headers)
    processo = (await criar_processo(client, funcionario_headers, cliente_id)).json()

    hoje = date.today()
    # dentro da antecedência (3 dias)
    await client.post(
        f"/processos/{processo['id']}/prazos",
        json={"data_prazo": str(hoje + timedelta(days=3)), "tipo": "peremptorio", "responsavel_id": responsavel_id},
        headers=funcionario_headers,
    )
    # fora de qualquer antecedência configurada
    await client.post(
        f"/processos/{processo['id']}/prazos",
        json={"data_prazo": str(hoje + timedelta(days=20)), "tipo": "peremptorio", "responsavel_id": responsavel_id},
        headers=funcionario_headers,
    )

    enviados = await alertas._executar()

    assert enviados == 1
    assert len(emails_enviados) == 1
    assert emails_enviados[0][0] == "funcionario@example.com"
    assert "3 dia" in emails_enviados[0][1]


async def test_alerta_usa_advogado_responsavel_do_processo_quando_prazo_sem_responsavel(
    client, funcionario_headers, session_maker, monkeypatch
):
    monkeypatch.setattr("app.tasks.alertas.AsyncSessionLocal", session_maker)

    emails_enviados = []
    monkeypatch.setattr(
        "app.tasks.alertas.enviar_email",
        lambda destinatario, assunto, corpo_html: emails_enviados.append(destinatario),
    )

    me = await client.get("/auth/me", headers=funcionario_headers)
    advogado_id = me.json()["id"]

    cliente_id = await criar_cliente(client, funcionario_headers)
    processo_resp = await client.post(
        "/processos",
        json={
            "numero_cnj": "0000001-39.2024.8.26.0100",
            "cliente_id": cliente_id,
            "advogado_responsavel_id": advogado_id,
        },
        headers=funcionario_headers,
    )
    processo = processo_resp.json()

    await client.post(
        f"/processos/{processo['id']}/prazos",
        json={"data_prazo": str(date.today() + timedelta(days=5)), "tipo": "peremptorio"},
        headers=funcionario_headers,
    )

    enviados = await alertas._executar()

    assert enviados == 1
    assert emails_enviados == ["funcionario@example.com"]


async def test_sem_destinatario_nao_envia_email(client, funcionario_headers, session_maker, monkeypatch):
    monkeypatch.setattr("app.tasks.alertas.AsyncSessionLocal", session_maker)
    enviados_chamadas = []
    monkeypatch.setattr("app.tasks.alertas.enviar_email", lambda *a: enviados_chamadas.append(a))

    cliente_id = await criar_cliente(client, funcionario_headers)
    processo = (await criar_processo(client, funcionario_headers, cliente_id)).json()
    await client.post(
        f"/processos/{processo['id']}/prazos",
        json={"data_prazo": str(date.today() + timedelta(days=10)), "tipo": "peremptorio"},
        headers=funcionario_headers,
    )

    enviados = await alertas._executar()

    assert enviados == 0
    assert enviados_chamadas == []


async def test_sincronizar_todos_processos_ativos_continua_apos_falha(
    client, funcionario_headers, session_maker, monkeypatch
):
    monkeypatch.setattr("app.tasks.sincronizacao.AsyncSessionLocal", session_maker)

    cliente_id = await criar_cliente(client, funcionario_headers)
    processo1 = (await criar_processo(client, funcionario_headers, cliente_id)).json()
    processo2 = (await criar_processo(client, funcionario_headers, cliente_id, numero=CNJ_VALIDO_2)).json()

    chamadas = []

    async def fake_consultar_processo(numero_cnj, tribunal, client=None):
        chamadas.append(numero_cnj)
        if numero_cnj == processo2["numero_cnj"]:
            raise DataJudError("falha simulada")
        return {"movimentos": [{"nome": "Despacho", "dataHora": "2026-06-01T09:00:00.000Z"}]}

    monkeypatch.setattr(
        "app.services.sincronizacao_service.datajud_service.consultar_processo", fake_consultar_processo
    )

    total = await sincronizacao._executar()

    assert total == 1
    assert len(chamadas) == 2

    movimentacoes = await client.get(f"/processos/{processo1['id']}/movimentacoes", headers=funcionario_headers)
    assert len(movimentacoes.json()) == 1

    processo2_atualizado = await client.get(f"/processos/{processo2['id']}", headers=funcionario_headers)
    assert processo2_atualizado.json()["ultima_consulta_datajud"] is None  # falhou antes de persistir
