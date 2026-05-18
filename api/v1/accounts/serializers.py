from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from apps.accounts.models import EmailOTP, TempUser, User
from api.v1.accounts.utils import generate_otp
from apps.accounts.tasks import send_otp_email_task


class SignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        email = value.lower().strip()

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already registered.")

        return email

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs

    def create(self, validated_data):
        email = validated_data["email"]

        temp_user, created = TempUser.objects.update_or_create(
            email=email,
            defaults={
                "first_name": validated_data["first_name"],
                "last_name": validated_data.get("last_name", ""),
                "phone_number": validated_data.get("phone_number", ""),
                "password": make_password(validated_data["password"]),
                "is_verified": False,
            },
        )

        EmailOTP.objects.filter(
            email=email,
            purpose=EmailOTP.Purpose.SIGNUP,
            is_verified=False,
        ).delete()

        otp = generate_otp()

        EmailOTP.objects.create(
            email=email,
            otp=otp,
            purpose=EmailOTP.Purpose.SIGNUP,
            expires_at=EmailOTP.default_expiry(),
        )

        send_otp_email_task.delay(
            email=email,
            otp=otp,
            purpose=EmailOTP.Purpose.SIGNUP,
        )

        return temp_user


class VerifySignupOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate_email(self, value):
        return value.lower().strip()

    def validate(self, attrs):
        email = attrs["email"]
        otp = attrs["otp"]

        try:
            temp_user = TempUser.objects.get(email=email, is_verified=False)
        except TempUser.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "Signup request not found. Please signup again."}
            )

        otp_obj = (
            EmailOTP.objects.filter(
                email=email,
                purpose=EmailOTP.Purpose.SIGNUP,
                is_verified=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not otp_obj:
            raise serializers.ValidationError(
                {"otp": "OTP not found. Please request a new OTP."}
            )

        if otp_obj.is_expired():
            raise serializers.ValidationError(
                {"otp": "OTP expired. Please request a new OTP."}
            )

        if otp_obj.attempts >= 5:
            raise serializers.ValidationError(
                {"otp": "Too many wrong attempts. Please request a new OTP."}
            )

        if otp_obj.otp != otp:
            otp_obj.attempts += 1
            otp_obj.save(update_fields=["attempts"])

            raise serializers.ValidationError(
                {"otp": "Invalid OTP."}
            )

        attrs["temp_user"] = temp_user
        attrs["otp_obj"] = otp_obj

        return attrs

    def create(self, validated_data):
        temp_user = validated_data["temp_user"]
        otp_obj = validated_data["otp_obj"]

        user = User.objects.create_user(
            email=temp_user.email,
            password=None,
            first_name=temp_user.first_name,
            last_name=temp_user.last_name,
            phone_number=temp_user.phone_number,
            role=User.Role.CUSTOMER,
            is_email_verified=True,
            is_active=True,
        )

        user.password = temp_user.password
        user.save(update_fields=["password"])

        otp_obj.is_verified = True
        otp_obj.save(update_fields=["is_verified"])

        temp_user.is_verified = True
        temp_user.save(update_fields=["is_verified"])

        EmailOTP.objects.filter(
            email=user.email,
            purpose=EmailOTP.Purpose.SIGNUP,
        ).exclude(id=otp_obj.id).delete()

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.lower().strip()

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        user = authenticate(
            username=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                {"detail": "Invalid email or password."}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "Your account is inactive."}
            )

        if not user.is_email_verified:
            raise serializers.ValidationError(
                {"detail": "Please verify your email before login."}
            )

        attrs["user"] = user

        return attrs


class UserBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "role",
            "is_email_verified",
        ]