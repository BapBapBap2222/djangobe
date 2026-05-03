from django.db.models import Q
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Agent
from .serializers import AgentDetailSerializer, AgentListSerializer


class AgentListView(generics.ListAPIView):
    serializer_class = AgentListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["full_name", "specialization", "city", "tagline", "bio"]

    def get_queryset(self):
        return Agent.objects.exclude(Q(user__is_staff=True) | Q(user__is_superuser=True))


class AgentDetailView(generics.RetrieveAPIView):
    serializer_class = AgentDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Agent.objects.exclude(Q(user__is_staff=True) | Q(user__is_superuser=True))


class AgentAdminBaseView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, slug: str) -> Agent:
        return Agent.objects.get(slug=slug)

    def check_admin(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Only administrators can manage agents."}, status=status.HTTP_403_FORBIDDEN)
        return None


class AgentRevokeVerificationView(AgentAdminBaseView):
    def post(self, request, slug: str):
        admin_error = self.check_admin(request)
        if admin_error:
            return admin_error

        try:
            agent = self.get_object(slug)
        except Agent.DoesNotExist:
            return Response({"detail": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)

        if not agent.is_verified:
            return Response({"detail": "Agent is already unverified."}, status=status.HTTP_400_BAD_REQUEST)

        agent.is_verified = False
        agent.save(update_fields=["is_verified", "updated_at"])
        return Response({"message": "Agent verification removed."}, status=status.HTTP_200_OK)


class AgentDeleteView(AgentAdminBaseView):
    def delete(self, request, slug: str):
        admin_error = self.check_admin(request)
        if admin_error:
            return admin_error

        try:
            agent = self.get_object(slug)
        except Agent.DoesNotExist:
            return Response({"detail": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)

        agent.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
