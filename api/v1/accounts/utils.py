import random

from rest_framework_simplejwt.tokens import RefreshToken


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp, purpose):
    """
    Temporary development email sender.

    For now, we print OTP in terminal.
    Later, we will replace this with real email sending.
    """
    print("=" * 60)
    print(f"OTP Purpose: {purpose}")
    print(f"Email: {email}")
    print(f"OTP: {otp}")
    print("=" * 60)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }