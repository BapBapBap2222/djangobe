from django.contrib import admin

from .models import Favorite, Property, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 0
    fields = ("image", "caption", "is_primary", "order")
    readonly_fields = ()


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner",
        "city",
        "district",
        "property_type",
        "listing_type",
        "status",
        "price",
        "is_active",
        "is_featured",
        "created_at",
    )
    list_filter = (
        "status",
        "property_type",
        "listing_type",
        "city",
        "is_active",
        "is_featured",
        "created_at",
    )
    search_fields = ("title", "address", "city", "district", "owner__username", "owner__email")
    inlines = [PropertyImageInline]


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "is_primary", "order")
    list_filter = ("is_primary",)
    search_fields = ("property__title", "caption")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "property", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "property__title")
