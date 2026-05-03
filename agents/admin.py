from django.contrib import admin

from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "city", "specialization", "rating", "total_reviews", "is_verified")
    list_filter = ("is_verified", "city")
    search_fields = ("full_name", "user__username", "user__email", "specialization", "city", "email", "phone")
    prepopulated_fields = {"slug": ("full_name",)}
