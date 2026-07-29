import uuid
from datetime import date, timedelta

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import StatusPublicacao
from app.models.publicacao import Publicacao
from app.services import djen_service, processo_service


async def get_by_id(db: AsyncSession, publicacao_id: uuid.UUID) -> Publicacao | None:
    result = await db.execute(
        select(Publicacao).where(Publicacao.id == publicacao_id).options(selectinload(Publicacao.processo))
    )
    return result.scalar_one_or_none()


async def list_publicacoes(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    status: StatusPublicacao | None = None,
    sigla_tribunal: str | None = None,
    processo_id: uuid.UUID | None = None,
) -> tuple[list[Publicacao], int]:
    query = select(Publicacao)
    if status is not None:
        query = query.where(Publicacao.status == status)
    if sigla_tribunal:
        query = query.where(Publicacao.sigla_tribunal == sigla_tribunal)
    if processo_id is not None:
        query = query.where(Publicacao.processo_id == processo_id)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()

    result = await db.execute(
        query.options(selectinload(Publicacao.processo))
        .order_by(Publicacao.data_disponibilizacao.desc(), Publicacao.id_djen.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(result.scalars().all()), total


async def resumo(db: AsyncSession) -> dict:
    contagens = {}
    for status in StatusPublicacao:
        result = await db.execute(
            select(func.count()).select_from(Publicacao).where(Publicacao.status == status)
        )
        contagens[status.value] = result.scalar_one()

    hoje = date.today()
    nao_tratadas_hoje = await db.execute(
        select(func.count())
        .select_from(Publicacao)
        .where(Publicacao.status == StatusPublicacao.NAO_TRATADA, Publicacao.data_disponibilizacao == hoje)
    )

    return {
        "nao_tratadas": contagens["nao_tratada"],
        "tratadas": contagens["tratada"],
        "descartadas": contagens["descartada"],
        "nao_tratadas_hoje": nao_tratadas_hoje.scalar_one(),
    }


async def sincronizar(
    db: AsyncSession,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    client: httpx.AsyncClient | None = None,
) -> list[Publicacao]:
    """Consulta o DJEN para todas as OABs configuradas e grava as comunicações novas.
    Idempotente: comunicações já importadas (mesmo id_djen) são ignoradas.
    Vincula automaticamente ao processo cadastrado quando o número CNJ bate."""
    fim = data_fim or date.today()
    inicio = data_inicio or (fim - timedelta(days=7))

    novas: list[Publicacao] = []
    for numero_oab, uf_oab in djen_service.oabs_configuradas():
        comunicacoes = await djen_service.consultar_comunicacoes(
            numero_oab, uf_oab, inicio, fim, client=client
        )

        for item in comunicacoes:
            id_djen = item.get("id")
            if id_djen is None:
                continue

            ja_existe = await db.execute(select(Publicacao.id).where(Publicacao.id_djen == id_djen))
            if ja_existe.scalar_one_or_none() is not None:
                continue

            numero_processo = item.get("numero_processo") or None
            processo = (
                await processo_service.get_by_numero_cnj(db, numero_processo) if numero_processo else None
            )

            data_str = item.get("data_disponibilizacao")
            publicacao = Publicacao(
                id_djen=id_djen,
                data_disponibilizacao=date.fromisoformat(data_str) if data_str else fim,
                sigla_tribunal=item.get("siglaTribunal"),
                tipo_comunicacao=item.get("tipoComunicacao"),
                tipo_documento=item.get("tipoDocumento"),
                nome_orgao=item.get("nomeOrgao"),
                nome_classe=item.get("nomeClasse"),
                numero_processo=numero_processo,
                texto=item.get("texto"),
                link=item.get("link"),
                meio=item.get("meiocompleto") or item.get("meio"),
                oab_numero=numero_oab,
                oab_uf=uf_oab,
                processo_id=processo.id if processo else None,
            )
            db.add(publicacao)
            novas.append(publicacao)

    await db.commit()
    return novas


async def atualizar_status(
    db: AsyncSession,
    publicacao: Publicacao,
    status: StatusPublicacao,
    usuario_id: uuid.UUID,
) -> Publicacao:
    publicacao.status = status
    publicacao.tratada_por_id = usuario_id if status != StatusPublicacao.NAO_TRATADA else None
    await db.commit()
    return await get_by_id(db, publicacao.id)
