import asyncio
import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_PORT = 465

"""
File contains functions for sending the password reset email
"""

class MailError(Exception):
    def __init__(self, cause: Exception):
        super().__init__(cause)


def _send_mail(
        receiver_email: str,
        message: str
) -> None:
    """
    Send email to defined receiver
    """
    try:
        password = os.environ.get("FASTAPI_SMTP_PASSWORD", "")
        sender_email = os.environ.get("FASTAPI_SMTP_ADDRESS", "")
        host = os.environ.get("FASTAPI_SMTP_HOST", "")

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(host, SMTP_PORT, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
    except smtplib.SMTPException as e:
        raise MailError(e)


def send_reset_password(
        receiver_email: str,
        token: str
) -> None:
    """
    Send email with password resetting
    """
    base_url = os.environ.get("FRONTEND_URL", "localhost")

    plain = f"""\
    A password reset request was received for your account. Please click the link below to proceed:
    {base_url}/reset-password?token={token}

    If you did not request a password reset, you can safely ignore this email.
    """

    html = f"""\
    <html>
      <body>
        <p>A password reset request was received for your account. Please click the link below to proceed:<br>
           <a href="{base_url}/reset-password?token={token}">{base_url}/reset-password</a>
           <br>
           <br>
            If you did not request a password reset, you can safely ignore this email.
        </p>
      </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = "Password reset"
    message["From"] = os.environ.get("FASTAPI_SMTP_ADDRESS")
    message["To"] = receiver_email

    part1 = MIMEText(plain, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        None, _send_mail, receiver_email, message.as_string()
    )
