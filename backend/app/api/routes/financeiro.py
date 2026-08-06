import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permissao
from app.core.database import get_db
from app.models.enums import ModuloSistema
from app.schemas.contrato_honorario import ContratoHonorarioCreate, ContratoHonorarioRead
from app.schemas.despesa import DespesaCreate, DespesaRead
from app.schemas.financeiro import RelatorioDespesas, RelatorioReceitas, SaldoProcesso
from app.schemas.parcela import ParcelaRead, ParcelaUpdate
from app.services import cliente_service, despesa_service, financeiro_service, honorario_service, pdf_service, processo_service

router = APIRouter(tags=["financeiro"])

_visualizar = Depends(require_permissao(ModuloSistema.FINANCEIRO, "visualizar"))
_editar = Depends(require_permissao(ModuloSistema.FINANCEIRO, "editar"))


@router.post(
    "/contratos-honorarios",
    response_model=ContratoHonorarioRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[_editar],
)
async def create_contrato(
    data: ContratoHonorarioCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ContratoHonorarioRead:
    if await cliente_service.get_by_id(db, data.cliente_id) is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cliente não encontrado")
    if data.processo_id is not None and await processo_service.get_by_id(db, data.processo_id) is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Processo não encontrado")
    return await honorario_service.create_contrato(db, data)


@router.get("/contratos-honorarios", response_model=list[ContratoHonorarioRead], dependencies=[_visualizar])
async def list_contratos(
    db: Annotated[AsyncSession, Depends(get_db)],
    cliente_id: uuid.UUID | None = None,
    processo_id: uuid.UUID | None = None,
) -> list[ContratoHonorarioRead]:
    return await honorario_service.list_contratos(db, cliente_id=cliente_id, processo_id=processo_id)


@router.get(
    "/contratos-honorarios/{contrato_id}", response_model=ContratoHonorarioRead, dependencies=[_visualizar]
)
async def get_contrato(contrato_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> ContratoHonorarioRead:
    contrato = await honorario_service.get_by_id(db, contrato_id)
    if contrato is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato não encontrado")
    return contrato


@router.patch("/parcelas/{parcela_id}", response_model=ParcelaRead, dependencies=[_editar])
async def update_parcela(
    parcela_id: uuid.UUID,
    data: ParcelaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ParcelaRead:
    parcela = await honorario_service.get_parcela(db, parcela_id)
    if parcela is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parcela não encontrada")
    return await honorario_service.update_parcela(db, parcela, data)


@router.post("/parcelas/{parcela_id}/pagamento", response_model=ParcelaRead, dependencies=[_editar])
async def registrar_pagamento(
    parcela_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    data_pagamento: date | None = None,
) -> ParcelaRead:
    parcela = await honorario_service.get_parcela(db, parcela_id)
    if parcela is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parcela não encontrada")
    return await honorario_service.registrar_pagamento(db, parcela, data_pagamento)


@router.get("/parcelas/{parcela_id}/recibo", dependencies=[_visualizar])
async def recibo_parcela(parcela_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> Response:
    parcela = await honorario_service.get_parcela_com_relacionamentos(db, parcela_id)
    if parcela is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parcela não encontrada")
    if parcela.data_pagamento is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parcela ainda não foi paga")

    pdf_bytes = pdf_service.gerar_recibo_parcela(parcela)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="recibo_parcela_{parcela.numero_parcela}.pdf"'},
    )


@router.post(
    "/processos/{processo_id}/despesas",
    response_model=DespesaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[_editar],
)
async def create_despesa(
    processo_id: uuid.UUID,
    data: DespesaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DespesaRead:
    if await processo_service.get_by_id(db, processo_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processo não encontrado")
    return await despesa_service.create_despesa(db, processo_id, data)


@router.get("/despesas", response_model=list[DespesaRead], dependencies=[_visualizar])
async def list_despesas(
    db: Annotated[AsyncSession, Depends(get_db)],
    processo_id: uuid.UUID | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[DespesaRead]:
    return await despesa_service.list_despesas(
        db, processo_id=processo_id, data_inicio=data_inicio, data_fim=data_fim
    )


@router.get("/processos/{processo_id}/saldo", response_model=SaldoProcesso, dependencies=[_visualizar])
async def saldo_processo(processo_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> SaldoProcesso:
    if await processo_service.get_by_id(db, processo_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processo não encontrado")
    return await financeiro_service.saldo_processo(db, processo_id)


@router.get("/relatorios/receitas", response_model=RelatorioReceitas, dependencies=[_visualizar])
async def relatorio_receitas(
    db: Annotated[AsyncSession, Depends(get_db)],
    cliente_id: uuid.UUID | None = None,
    processo_id: uuid.UUID | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> RelatorioReceitas:
    return await financeiro_service.relatorio_receitas(
        db, cliente_id=cliente_id, processo_id=processo_id, data_inicio=data_inicio, data_fim=data_fim
    )


@router.get("/relatorios/despesas", response_model=RelatorioDespesas, dependencies=[_visualizar])
async def relatorio_despesas(
    db: Annotated[AsyncSession, Depends(get_db)],
    processo_id: uuid.UUID | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> RelatorioDespesas:
    return await financeiro_service.relatorio_despesas(
        db, processo_id=processo_id, data_inicio=data_inicio, data_fim=data_fim
    )
