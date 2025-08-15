import aiosmtplib, email.utils, uuid
from email.message import EmailMessage
from jinja2 import Template
from .config import settings

def render_email_html(body_html: str, pixel_url: str, unsubscribe_url: str, sender_name: str, lead: dict) -> str:
    # Using a simple inline template loader for brevity (file template exists too).
    with open("app/templates/email.html.j2", "r", encoding="utf-8") as f:
        template = Template(f.read())
    return template.render(body_html=body_html, pixel_url=pixel_url, unsubscribe_url=unsubscribe_url, sender_name=sender_name, lead=lead)

async def send_email(to_email: str, subject: str, html: str) -> str:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid()
    msg.set_content("This email requires an HTML-capable client.")
    msg.add_alternative(html, subtype="html")

    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        start_tls=True,
        username=settings.smtp_username,
        password=settings.smtp_password,
    )
    return msg["Message-ID"]
