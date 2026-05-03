from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils import timezone
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from agents.models import Agent
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import VerificationRequest
from .serializers import (
    AdminVerificationRequestSerializer,
    ChangePasswordSerializer,
    ForgotPasswordRequestSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    VerificationDecisionSerializer,
    VerificationRequestSerializer,
)
from .services import AuthService


password_reset_token_generator = PasswordResetTokenGenerator()


class IsStaffUser(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(super().has_permission(request, view) and request.user.is_staff)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = AuthService.register(serializer.validated_data)
        return Response(tokens, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = AuthService.login(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        return Response(result)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token")},
            required=["refresh"],
        )
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."})
        except Exception:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_object(self):
        return self.request.user.profile


class VerificationRequestView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get(self, request):
        latest = request.user.verification_requests.order_by("-created_at").first()
        if not latest:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(VerificationRequestSerializer(latest, context={"request": request}).data)

    def post(self, request):
        agent = Agent.objects.filter(user=request.user).first()
        if agent and agent.is_verified:
            return Response({"detail": "This account is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.verification_requests.filter(status=VerificationRequest.Status.PENDING).exists():
            return Response({"detail": "You already have a pending verification request."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = VerificationRequestSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        verification_request = serializer.save(
            user=request.user,
            status=VerificationRequest.Status.PENDING,
            denial_reason="",
            reviewed_by=None,
            reviewed_at=None,
        )
        return Response(
            VerificationRequestSerializer(verification_request, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AdminVerificationRequestListView(generics.ListAPIView):
    permission_classes = [IsStaffUser]
    serializer_class = AdminVerificationRequestSerializer

    def get_queryset(self):
        queryset = VerificationRequest.objects.select_related("user").order_by("-created_at")
        status_filter = self.request.query_params.get("status")
        search = (self.request.query_params.get("search") or "").strip()
        if status_filter in {
            VerificationRequest.Status.PENDING,
            VerificationRequest.Status.APPROVED,
            VerificationRequest.Status.DENIED,
        }:
            queryset = queryset.filter(status=status_filter)
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search)
                | Q(user__email__icontains=search)
                | Q(full_name__icontains=search)
            )
        return queryset


class AdminVerificationDecisionView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, pk: int):
        try:
            verification_request = VerificationRequest.objects.select_related("user").get(pk=pk)
        except VerificationRequest.DoesNotExist:
            return Response({"detail": "Verification request not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = VerificationDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]
        denial_reason = serializer.validated_data.get("denial_reason", "").strip()

        verification_request.reviewed_by = request.user
        verification_request.reviewed_at = timezone.now()

        agent = Agent.objects.filter(user=verification_request.user).first()

        if action == "accept":
            verification_request.status = VerificationRequest.Status.APPROVED
            verification_request.denial_reason = ""
            if agent:
                agent.is_verified = True
                agent.save(update_fields=["is_verified", "updated_at"])
        else:
            verification_request.status = VerificationRequest.Status.DENIED
            verification_request.denial_reason = denial_reason
            if agent and agent.is_verified:
                agent.is_verified = False
                agent.save(update_fields=["is_verified", "updated_at"])

        verification_request.save()
        return Response(AdminVerificationRequestSerializer(verification_request, context={"request": request}).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.change_password(
            user=request.user,
            old_password=serializer.validated_data["old_password"],
            new_password=serializer.validated_data["new_password"],
        )
        return Response({"message": "Password changed successfully."})


class ForgotPasswordRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"].strip()
        email = serializer.validated_data["email"].strip().lower()

        user = User.objects.filter(username=username, email__iexact=email, is_active=True).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = password_reset_token_generator.make_token(user)
            reset_link = f"{settings.FRONTEND_BASE_URL}/reset-password/confirm?uid={uid}&token={token}"

            send_mail(
                subject="Reset your Blue Sky password",
                message=(
                    "We received a request to reset your Blue Sky account password.\n\n"
                    f"Open this link to choose a new password:\n{reset_link}\n\n"
                    f"This link expires in {settings.PASSWORD_RESET_TIMEOUT // 60} minutes.\n"
                    "If you did not request this, you can ignore this email."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response(
            {
                "message": (
                    "If the username and email match an account, a password reset link has been sent."
                )
            }
        )


class PasswordResetTokenValidateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = (request.query_params.get("uid") or "").strip()
        token = (request.query_params.get("token") or "").strip()
        if not uid or not token:
            return Response({"valid": False, "detail": "Missing reset token."}, status=status.HTTP_400_BAD_REQUEST)

        user = AuthService.get_user_from_reset_uid(uid)
        is_valid = bool(user and password_reset_token_generator.check_token(user, token))
        if not is_valid:
            return Response({"valid": False, "detail": "This reset link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"valid": True})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"].strip()
        token = serializer.validated_data["token"].strip()
        user = AuthService.get_user_from_reset_uid(uid)
        if not user or not password_reset_token_generator.check_token(user, token):
            raise ValidationError("This reset link is invalid or has expired.")

        AuthService.set_new_password(
            user=user,
            new_password=serializer.validated_data["new_password"],
        )
        return Response({"message": "Password reset successfully."})
