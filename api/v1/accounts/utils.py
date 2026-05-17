from django.core.mail import send_mail
from django.conf import settings
import random

from rest_framework_simplejwt.tokens import RefreshToken


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp, purpose):
    subject_map = {
        "SIGNUP": "Verify your UrbanFit account",
        "FORGOT_PASSWORD": "Reset your UrbanFit password",
    }

    subject = subject_map.get(purpose, "Your UrbanFit verification code")

    message = (
        f"Hello,\n\n"
        f"Your UrbanFit verification code is: {otp}\n\n"
        f"This code will expire in 10 minutes.\n\n"
        f"If you did not request this code, please ignore this email.\n\n"
        f"Regards,\n"
        f"UrbanFit Team"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }