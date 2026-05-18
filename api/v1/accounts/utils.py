import random

import resend
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp, purpose):
    subject_map = {
        "SIGNUP": "Verify your UrbanFit account",
        "FORGOT_PASSWORD": "Reset your UrbanFit password",
    }

    subject = subject_map.get(purpose, "Your UrbanFit verification code")

    html_content = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2>UrbanFit Verification Code</h2>
            <p>Hello,</p>
            <p>Your UrbanFit verification code is:</p>
            <h1 style="letter-spacing: 4px;">{otp}</h1>
            <p>This code will expire in 10 minutes.</p>
            <p>If you did not request this code, please ignore this email.</p>
            <br>
            <p>Regards,<br>UrbanFit Team</p>
        </div>
    """

    text_content = (
        f"Hello,\n\n"
        f"Your UrbanFit verification code is: {otp}\n\n"
        f"This code will expire in 10 minutes.\n\n"
        f"If you did not request this code, please ignore this email.\n\n"
        f"Regards,\n"
        f"UrbanFit Team"
    )

    return resend.Emails.send(
        {
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [email],
            "subject": subject,
            "html": html_content,
            "text": text_content,
        }
    )


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }