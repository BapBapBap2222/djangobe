from django.contrib import admin

from .models import UserProfile, VerificationRequest


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__username", "user__email", "phone")


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "status", "reviewed_by", "created_at")
    list_filter = ("status", "gender", "created_at", "reviewed_at")
    search_fields = ("user__username", "user__email", "full_name", "national_id_number")
