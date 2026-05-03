from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken


class AuthService:
    @staticmethod
    def register(validated_data: dict) -> dict:
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return AuthService._make_tokens(user)

    @staticmethod
    def login(username: str, password: str) -> dict:
        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed("Invalid username or password.")
        if not user.is_active:
            raise AuthenticationFailed("This account has been disabled.")

        tokens = AuthService._make_tokens(user)
        tokens["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.get_full_name(),
        }
        return tokens

    @staticmethod
    def change_password(user, old_password: str, new_password: str) -> None:
        if not user.check_password(old_password):
            raise ValidationError("Current password is incorrect.")
        user.set_password(new_password)
        user.save()

    @staticmethod
    def set_new_password(user, new_password: str) -> None:
        user.set_password(new_password)
        user.save(update_fields=["password"])

    @staticmethod
    def get_user_from_reset_uid(uid: str):
        try:
            user_id = urlsafe_base64_decode(uid).decode()
            return User.objects.filter(pk=user_id, is_active=True).first()
        except Exception:
            return None

    @staticmethod
    def _make_tokens(user) -> dict:
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
