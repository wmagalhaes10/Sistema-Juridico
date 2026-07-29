from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import OrigemMovimentacao, TipoPrazo
from app.models.movimentacao import Movimentacao
from app.models.prazo import Prazo
from app.models.processo import Processo
from app.services import datajud_service, feriado_service

# termos que disparam criação automática de prazo e o nº de dias úteis padrão de cada um
GATILHOS_PRAZO: dict[str, int] = {
    "intimação": 15,
    "intimacao": 15,
    "citação": 15,
    "citacao": 15,
    "despacho": 5,
    "sentença": 15,
    "sentenca": 15,
}


def _detectar_gatilho(descricao: str) -> int | None:
    texto = descricao.lower()
    for termo, dias in GATILHOS_PRAZO.items():
        if termo in texto:
            return dias
    return None


async def sincronizar_processo(
    db: AsyncSession, processo: Processo, client: httpx.AsyncClient | None = None
) -> list[Movimentacao]:
    dados = await datajud_service.consultar_processo(processo.numero_cnj, processo.tribunal or "", client=client)
    processo.ultima_consulta_datajud = datetime.now(timezone.utc)

    novas_movimentacoes: list[Movimentacao] = []

    for mov in dados.get("movimentos", []):
        data_str = mov.get("dataHora")
        descricao = mov.get("nome")
        if not data_str or not descricao:
            continue
        data_mov = datetime.fromisoformat(data_str.replace("Z", "+00:00"))

        ja_existe = await db.execute(
            select(Movimentacao).where(
                Movimentacao.processo_id == processo.id,
                Movimentacao.data_movimentacao == data_mov,
                Movimentacao.descricao == descricao,
            )
        )
        if ja_existe.scalar_one_or_none() is not None:
            continue

        movimentacao = Movimentacao(
            processo_id=processo.id,
            data_movimentacao=data_mov,
            descricao=descricao,
            origem=OrigemMovimentacao.DATAJUD,
        )
        db.add(movimentacao)
        await db.flush()
        novas_movimentacoes.append(movimentacao)

        dias_prazo = _detectar_gatilho(descricao)
        if dias_prazo is not None:
            data_prazo = await feriado_service.adicionar_dias_uteis(db, data_mov.date(), dias_prazo)
            db.add(
                Prazo(
                    processo_id=processo.id,
                    movimentacao_origem_id=movimentacao.id,
                    responsavel_id=processo.advogado_responsavel_id,
                    data_prazo=data_prazo,
                    tipo=TipoPrazo.PEREMPTORIO,
                    descricao=f"Prazo gerado automaticamente a partir de: {descricao}",
                )
            )

    await db.commit()
    return novas_movimentacoes
