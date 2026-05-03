from django.db.models import Q
from rest_framework import filters, generics

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
