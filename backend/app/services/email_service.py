import smtplib
from email.mime.text import MIMEText

import httpx

from app.core.config import settings


def enviar_email(destinatario: str, assunto: str, corpo_html: str) -> None:
    if settings.SENDGRID_API_KEY:
        _enviar_via_sendgrid(destinatario, assunto, corpo_html)
    else:
        _enviar_via_smtp(destinatario, assunto, corpo_html)


def _enviar_via_smtp(destinatario: str, assunto: str, corpo_html: str) -> None:
    mensagem = MIMEText(corpo_html, "html", "utf-8")
    mensagem["Subject"] = assunto
    mensagem["From"] = settings.SMTP_FROM or settings.SMTP_USER
    mensagem["To"] = destinatario

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as servidor:
        servidor.starttls()
        if settings.SMTP_USER:
            servidor.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        servidor.send_message(mensagem)


def _enviar_via_sendgrid(destinatario: str, assunto: str, corpo_html: str) -> None:
    response = httpx.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "personalizations": [{"to": [{"email": destinatario}]}],
            "from": {"email": settings.SMTP_FROM or settings.SMTP_USER},
            "subject": assunto,
            "content": [{"type": "text/html", "value": corpo_html}],
        },
        timeout=10,
    )
    response.raise_for_status()
