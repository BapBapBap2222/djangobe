from rest_framework import serializers

from properties.models import Property

from .models import Agent


def get_visible_properties_for_agent(agent: Agent):
    if not agent.user_id:
        return Property.objects.none()

    return (
        Property.objects.filter(owner=agent.user, is_active=True)
        .prefetch_related("images")
        .order_by("-created_at")
    )


def get_property_image_url(property_obj: Property, request):
    image = property_obj.images.filter(is_primary=True).first() or property_obj.images.first()
    if not image:
        return None
    return request.build_absolute_uri(image.image.url) if request else image.image.url


class AgentListSerializer(serializers.ModelSerializer):
    areas = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = [
            "id",
            "full_name",
            "slug",
            "avatar_url",
            "city",
            "specialization",
            "tagline",
            "years_experience",
            "total_listings",
            "deals_closed",
            "rating",
            "total_reviews",
            "is_verified",
            "response_time",
            "areas",
            "languages",
        ]

    def get_areas(self, agent: Agent):
        if agent.user_id:
            cities = []
            for property_obj in get_visible_properties_for_agent(agent):
                city = (property_obj.city or "").strip()
                if city and city not in cities:
                    cities.append(city)
                if len(cities) >= 5:
                    break
            if cities:
                return cities
        return (agent.areas or [])[:5]


class AgentDetailSerializer(serializers.ModelSerializer):
    areas = serializers.SerializerMethodField()
    activity_visible = serializers.SerializerMethodField()
    latest_activities = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = [
            "id",
            "full_name",
            "slug",
            "avatar_url",
            "email",
            "phone",
            "city",
            "specialization",
            "tagline",
            "years_experience",
            "total_listings",
            "deals_closed",
            "rating",
            "total_reviews",
            "is_verified",
            "response_time",
            "areas",
            "languages",
            "bio",
            "activity_visible",
            "latest_activities",
            "created_at",
            "updated_at",
        ]

    def get_areas(self, agent: Agent):
        if agent.user_id:
            cities = []
            for property_obj in get_visible_properties_for_agent(agent):
                city = (property_obj.city or "").strip()
                if city and city not in cities:
                    cities.append(city)
                if len(cities) >= 5:
                    break
            if cities:
                return cities
        return (agent.areas or [])[:5]

    def get_activity_visible(self, agent: Agent):
        profile = getattr(agent.user, "profile", None) if agent.user_id else None
        return bool(profile.activity_visible) if profile else False

    def get_latest_activities(self, agent: Agent):
        profile = getattr(agent.user, "profile", None) if agent.user_id else None
        if not profile or not profile.activity_visible:
            return []

        request = self.context.get("request")
        activities = []
        for property_obj in get_visible_properties_for_agent(agent)[:2]:
            activities.append(
                {
                    "id": property_obj.id,
                    "title": property_obj.title,
                    "label": "New listing",
                    "listing_type": property_obj.get_listing_type_display(),
                    "address": ", ".join(
                        part for part in [property_obj.address, property_obj.district, property_obj.city] if part
                    ),
                    "created_at": property_obj.created_at,
                    "image": get_property_image_url(property_obj, request),
                }
            )
        return activities
