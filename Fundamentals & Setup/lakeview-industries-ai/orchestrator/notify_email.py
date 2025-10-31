from __future__ import annotations
import os
from typing import Optional
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
except Exception:
    SendGridAPIClient = None  # type: ignore
    Mail = None  # type: ignore

from orchestrator.config import load_env
SETTINGS = load_env()

def notify_supervisor(state) -> Optional[str]:
    subject = f"[IronPath] {state.session_id} {state.machine_area or ''} — update".strip()
    bluf_line = (state.proposed_steps or "").splitlines()[0] if state.proposed_steps else "(no BLUF)"
    link = state.log_ref or "(no report link)"
    body = f"{bluf_line}\n\nStatus: {state.status}\nReport: {link}\n"
    to_emails = [e.strip() for e in (SETTINGS.SUPERVISOR_EMAIL or "").split(",") if e.strip()]

    if not to_emails or not SETTINGS.FROM_EMAIL:
        return "(email not configured)"

    if SendGridAPIClient is None or Mail is None or not os.getenv("SENDGRID_API_KEY"):
        return f"(dev) Would email {to_emails}: {subject} -> {body[:120]}..."

    message = Mail(
        from_email=SETTINGS.FROM_EMAIL,
        to_emails=to_emails,
        subject=subject,
        plain_text_content=body,
    )
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        resp = sg.send(message)
        return f"Sent email: {resp.status_code}"
    except Exception as e:
        return f"Email error: {e}"
