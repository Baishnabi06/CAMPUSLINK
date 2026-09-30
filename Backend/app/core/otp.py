import hashlib
import hmac
import secrets
import smtplib
from email.message import EmailMessage

from app.config import settings


def generate_otp() -> str:
    """Cryptographically secure 6-digit code (leading zeros kept)."""
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(email: str, otp: str) -> str:
    """Keyed hash, so a leaked database doesn't reveal usable codes."""
    return hmac.new(
        settings.jwt_secret_key.encode(),
        f"{email}:{otp}".encode(),
        hashlib.sha256,
    ).hexdigest()


def send_otp_email(to_email: str, otp: str) -> None:
    if not settings.smtp_user or not settings.smtp_password:
        raise RuntimeError(
            "SMTP is not configured. Set SMTP_USER and SMTP_PASSWORD in .env."
        )

    msg = EmailMessage()
    msg["Subject"] = "Your CampusLink login code"
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = to_email
    msg.set_content(
        f"Your CampusLink login code is {otp}.\n\n"
        f"It expires in {settings.otp_expire_minutes} minutes. "
        f"If you didn't request it, you can ignore this email."
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)