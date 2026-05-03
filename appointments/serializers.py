from django.utils import timezone
from rest_framework import serializers

from .models import Appointment, AppointmentStatus


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Appointment DTO.
    """

    property_title = serializers.CharField(source="property.title", read_only=True)
    property_owner = serializers.CharField(source="property.owner.username", read_only=True)
    property_address = serializers.CharField(source="property.address", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "property",
            "property_title",
            "property_owner",
            "property_address",
            "date",
            "time",
            "name",
            "phone",
            "message",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]

    def validate(self, data):
        request = self.context.get("request")
        appointment_date = data.get("date")
        appointment_time = data.get("time")
        property_obj = data.get("property")

        if appointment_date and appointment_date < timezone.localdate():
            raise serializers.ValidationError({"date": "Appointment date cannot be in the past."})

        if (
            appointment_date
            and appointment_time
            and appointment_date == timezone.localdate()
            and appointment_time <= timezone.localtime().time().replace(second=0, microsecond=0)
        ):
            raise serializers.ValidationError({"time": "Appointment time must be in the future."})

        if request and request.user and property_obj and property_obj.owner_id == request.user.id:
            raise serializers.ValidationError({"property": "You cannot book your own property."})

        if property_obj and (not property_obj.is_active or property_obj.status in {"inactive", "sold", "rented"}):
            raise serializers.ValidationError({"property": "This property is not available for appointments."})

        return data


class AppointmentStatusUpdateSerializer(serializers.Serializer):
    """
    DTO for appointment status update.
    """

    status = serializers.ChoiceField(
        choices=[
            (AppointmentStatus.CONFIRMED, "Confirmed"),
            (AppointmentStatus.REJECTED, "Rejected"),
            (AppointmentStatus.COMPLETED, "Completed"),
            (AppointmentStatus.CANCELLED, "Cancelled"),
        ]
    )
