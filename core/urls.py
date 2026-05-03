"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import: from my_app import views
    2. Add a URL to urlpatterns: path('', views.home, name='home')
Class-based views
    1. Add an import: from other_app.views import Home
    2. Add a URL to urlpatterns: path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns: path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


docs_permission_classes = (
    (permissions.AllowAny,)
    if settings.SWAGGER_PUBLIC
    else (permissions.IsAdminUser,)
)

schema_view = get_schema_view(
    openapi.Info(
        title="House Sell API",
        default_version="v1",
        description="Django REST Framework API for House Sell website",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@housesell.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=docs_permission_classes,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "accounts/login/",
        RedirectView.as_view(url="/admin/login/", permanent=False),
        name="login",
    ),
    path("api/auth/", include("accounts.urls")),
    path("api/agents/", include("agents.urls")),
    path("api/properties/", include("properties.urls")),
    path("api/appointments/", include("appointments.urls")),
    path("api/news/", include("news.urls")),
    path("api/prediction/", include("prediction.urls")),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
