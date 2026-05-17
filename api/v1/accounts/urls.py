from django.urls import path

from api.v1.accounts.views import (
    LoginAPIView,
    SignupAPIView,
    VerifySignupOTPAPIView,
)


urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("verify-signup-otp/", VerifySignupOTPAPIView.as_view(), name="verify_signup_otp"),
    path("login/", LoginAPIView.as_view(), name="login"),
]