from email.message import EmailMessage
import aiosmtplib
from app.config import settings

async def send_otp_email(to_email: str, otp_code: str):
    message = EmailMessage()
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = to_email
    message["Subject"] = "Verify Your IntelliDocs Account"
    
    body = (
        f"Welcome to IntelliDocs!\n\n"
        f"Your verification code is: {otp_code}\n\n"
        f"This code will expire in 10 minutes. If you did not register, please ignore this email."
    )
    message.set_content(body)

    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        # Fallback console logger for development testing without live SMTP credentials
        print(f"\n[DEV MODE] OTP Email sent to {to_email}. Code: {otp_code}\n")
        return

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        print(f"OTP Email sent successfully to {to_email}.")
    except Exception as e:
        print(f"Failed to send OTP email to {to_email}. Error: {e}")
        raise RuntimeError(f"Failed to send OTP email: {e}")
    