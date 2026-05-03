from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('name', 'phone', 'user__username', 'property__title')
