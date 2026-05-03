from django.db.models import Q
from rest_framework.exceptions import NotFound

from .models import Appointment


class AppointmentRepository:
    """
    Repository layer for Appointment queries.
    """

    @staticmethod
    def get_user_appointments(user):
        return Appointment.objects.filter(user=user).select_related("property", "property__owner")

    @staticmethod
    def get_owner_appointments(owner_user):
        return Appointment.objects.filter(property__owner=owner_user).select_related("property", "user")

    @staticmethod
    def get_actor_scope(actor):
        if getattr(actor, "is_staff", False):
            return Appointment.objects.select_related("property", "property__owner", "user")
        return Appointment.objects.filter(
            Q(user=actor) | Q(property__owner=actor)
        ).select_related("property", "property__owner", "user")

    @staticmethod
    def get_by_id(pk: int):
        try:
            return Appointment.objects.select_related("property", "property__owner", "user").get(pk=pk)
        except Appointment.DoesNotExist as exc:
            raise NotFound("Appointment not found.") from exc

    @staticmethod
    def create_appointment(data: dict) -> Appointment:
        return Appointment.objects.create(**data)
