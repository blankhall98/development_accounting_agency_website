from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.config import settings


def send_contact_email(to_email: str, name: str, email: str, message: str) -> tuple[bool, str]:
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        return False, "SMTP not configured"

    sender = settings.smtp_from or settings.smtp_user

    msg = EmailMessage()
    msg["Subject"] = f"Nuevo mensaje de {name}"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(f"Nombre: {name}\nEmail: {email}\n\nMensaje:\n{message}")

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        return True, "Sent"
    except Exception as exc:  # pragma: no cover - depends on SMTP
        return False, f"Error: {exc}"
