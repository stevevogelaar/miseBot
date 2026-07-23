"""Email composition and sending."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict


def build_shopping_email(items: List[Dict], to_email: str, from_email: str) -> str:
    """Build HTML email for shopping list."""
    rows = ""
    for item in items:
        name = item.get("name", "")
        qty = item.get("quantity", "")
        unit = item.get("unit", "")
        rows += f"<tr><td>{name}</td><td>{qty} {unit}</td></tr>\n"

    html = f"""
    <html>
    <head><style>
        body {{ font-family: Arial, sans-serif; font-size: 14px; color: #1A1A1A; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background: #C41E3A; color: white; font-weight: bold; }}
        h2 {{ color: #C41E3A; }}
    </style></head>
    <body>
        <h2>miseBot Shopping List</h2>
        <table>
            <tr><th>Item</th><th>Quantity</th></tr>
            {rows}
        </table>
        <p style="color:#888; font-size:12px;">Sent by miseBot — your AI Sous-Chef</p>
    </body>
    </html>
    """
    return html


def build_prep_email(items: List[Dict], to_email: str, from_email: str) -> str:
    """Build HTML email for prep list with checkbox column."""
    rows = ""
    for item in items:
        name = item.get("name", "")
        qty = item.get("quantity", "")
        unit = item.get("unit", "")
        status = item.get("status", "pending")
        check = "&#9745;" if status == "done" else "&#9744;"
        rows += f"<tr><td>{name}</td><td>{qty} {unit}</td><td>{status.title()}</td><td style='text-align:center;'>{check}</td></tr>\n"

    html = f"""
    <html>
    <head><style>
        body {{ font-family: Arial, sans-serif; font-size: 14px; color: #1A1A1A; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background: #C41E3A; color: white; font-weight: bold; }}
        .checkbox-col {{ width: 40px; text-align: center; }}
        h2 {{ color: #C41E3A; }}
    </style></head>
    <body>
        <h2>miseBot Prep List</h2>
        <table>
            <tr><th>Item</th><th>Quantity</th><th>Status</th><th class='checkbox-col'>&#9744;</th></tr>
            {rows}
        </table>
        <p style="color:#888; font-size:12px;">Sent by miseBot — your AI Sous-Chef<br>
        Print and check off items as you complete them.</p>
    </body>
    </html>
    """
    return html


def send_email(to_email: str, from_email: str, subject: str, html_body: str, smtp_config: Dict) -> bool:
    """Send email via SMTP."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        msg.attach(MIMEText(html_body, "html"))

        host = smtp_config.get("smtp_host", "smtp.gmail.com")
        port = smtp_config.get("smtp_port", 587)
        user = smtp_config.get("smtp_user", "")
        password = smtp_config.get("smtp_pass", "")

        with smtplib.SMTP(host, port) as server:
            server.starttls()
            if user and password:
                server.login(user, password)
            server.sendmail(from_email, [to_email], msg.as_string())
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False
