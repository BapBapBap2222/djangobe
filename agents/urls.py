from django.urls import path

from .views import AgentDeleteView, AgentDetailView, AgentListView, AgentRevokeVerificationView


urlpatterns = [
    path("", AgentListView.as_view(), name="agent-list"),
    path("<slug:slug>/revoke-verification/", AgentRevokeVerificationView.as_view(), name="agent-revoke-verification"),
    path("<slug:slug>/delete/", AgentDeleteView.as_view(), name="agent-delete"),
    path("<slug:slug>/", AgentDetailView.as_view(), name="agent-detail"),
]
