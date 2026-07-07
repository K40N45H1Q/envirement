import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


class AuthEmailError(Exception):
    pass


def send_auth_email(receiver_email: str, subject: str, body: str) -> None:
    username = settings.smtp_username
    password = settings.smtp_password
    host = settings.smtp_host
    from_email = settings.smtp_from_email or username

    if not username or not password or not host or not from_email:
        raise AuthEmailError("smtp_not_configured")

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain", "utf-8"))

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(host, settings.smtp_port, context=context) as server:
            server.login(username, password)
            server.sendmail(from_email, receiver_email, message.as_string())
    except Exception as exc:
        raise AuthEmailError("smtp_delivery_failed") from exc


def send_registration_code_email(receiver_email: str, code: str) -> None:
    send_auth_email(
        receiver_email,
        "CVHOLD verification code",
        (
            "Your CVHOLD verification code is: "
            f"{code}\n\n"
            f"This code expires in {settings.registration_code_expire_minutes} minutes."
        ),
    )


def send_password_reset_code_email(receiver_email: str, code: str) -> None:
    send_auth_email(
        receiver_email,
        "CVHOLD password reset code",
        (
            "Your CVHOLD password reset code is: "
            f"{code}\n\n"
            f"This code expires in {settings.password_reset_code_expire_minutes} minutes.\n"
            "If you did not request a password reset, you can safely ignore this email."
        ),
    )
