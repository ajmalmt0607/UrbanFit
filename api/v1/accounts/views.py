from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.accounts.serializers import (
    LoginSerializer,
    SignupSerializer,
    UserBasicSerializer,
    VerifySignupOTPSerializer,
)
from api.v1.accounts.utils import get_tokens_for_user


class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Signup started successfully. Please verify OTP sent to your email."
            },
            status=status.HTTP_201_CREATED,
        )


class VerifySignupOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifySignupOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = get_tokens_for_user(user)
        # user_data = UserBasicSerializer(user).data

        return Response(
            {
                "message": "Email verified successfully.",
                # "user": user_data,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        tokens = get_tokens_for_user(user)
        # user_data = UserBasicSerializer(user).data

        return Response(
            {
                "message": "Login successful.",
                # "user": user_data,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )