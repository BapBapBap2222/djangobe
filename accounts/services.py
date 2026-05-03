from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, ValidationError


class AuthService:
    """Toàn bộ business logic xác thực tập trung ở đây - Service Layer Pattern"""

    @staticmethod
    def register(validated_data: dict) -> dict:
        """Tạo user mới, UserProfile tự tạo qua Signal"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return AuthService._make_tokens(user)

    @staticmethod
    def login(username: str, password: str) -> dict:
        """Xác thực và trả về tokens + info user"""
        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed("Sai tài khoản hoặc mật khẩu!")
        if not user.is_active:
            raise AuthenticationFailed("Tài khoản đã bị vô hiệu hóa!")
        tokens = AuthService._make_tokens(user)
        tokens['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name(),
        }
        return tokens

    @staticmethod
    def change_password(user, old_password: str, new_password: str) -> None:
        """Đổi mật khẩu, raise lỗi nếu mật khẩu cũ sai"""
        if not user.check_password(old_password):
            raise ValidationError("Mật khẩu cũ không đúng!")
        user.set_password(new_password)
        user.save()

    @staticmethod
    def _make_tokens(user) -> dict:
        """Tạo cặp access + refresh token"""
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
