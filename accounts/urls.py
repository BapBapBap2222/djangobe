from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
    path('verification-request/', views.VerificationRequestView.as_view(), name='verification-request'),
    path('admin/verification-requests/', views.AdminVerificationRequestListView.as_view(), name='admin-verification-requests'),
    path('admin/verification-requests/<int:pk>/decision/', views.AdminVerificationDecisionView.as_view(), name='admin-verification-decision'),
    path('users/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
]
