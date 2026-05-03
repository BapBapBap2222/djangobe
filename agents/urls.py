from django.urls import path

from .views import AgentDetailView, AgentListView


urlpatterns = [
    path("", AgentListView.as_view(), name="agent-list"),
    path("<slug:slug>/", AgentDetailView.as_view(), name="agent-detail"),
]

