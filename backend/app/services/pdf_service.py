import io
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from app.models.parcela_honorario import ParcelaHonorario


def gerar_recibo_parcela(parcela: ParcelaHonorario) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    contrato = parcela.contrato
    cliente = contrato.cliente

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(largura / 2, altura - 3 * cm, "RECIBO DE PAGAMENTO DE HONORÁRIOS")

    c.setFont("Helvetica", 11)
    y = altura - 5 * cm
    linhas = [
        f"Cliente: {cliente.nome_razao_social}",
        f"CPF/CNPJ: {cliente.cpf_cnpj}",
        f"Tipo de contrato: {contrato.tipo.value}",
        f"Parcela: {parcela.numero_parcela}/{contrato.numero_parcelas}",
        f"Valor pago: R$ {parcela.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"Vencimento: {parcela.data_vencimento.strftime('%d/%m/%Y')}",
        f"Data do pagamento: {parcela.data_pagamento.strftime('%d/%m/%Y') if parcela.data_pagamento else '-'}",
    ]
    for linha in linhas:
        c.drawString(2.5 * cm, y, linha)
        y -= 0.8 * cm

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(2.5 * cm, 2 * cm, f"Emitido em {date.today().strftime('%d/%m/%Y')}")

    c.showPage()
    c.save()
    return buffer.getvalue()
