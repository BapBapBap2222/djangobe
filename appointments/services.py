from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import AppointmentStatus
from .repositories import AppointmentRepository


class AppointmentService:
    """
    Business logic for appointment lifecycle.
    """

    REQUESTER_CANCELABLE_STATUSES = {
        AppointmentStatus.PENDING,
        AppointmentStatus.CONFIRMED,
    }

    OWNER_ALLOWED_TRANSITIONS = {
        AppointmentStatus.PENDING: {
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.REJECTED,
        },
        AppointmentStatus.CONFIRMED: {
            AppointmentStatus.COMPLETED,
            AppointmentStatus.REJECTED,
        },
        AppointmentStatus.REJECTED: set(),
        AppointmentStatus.COMPLETED: set(),
        AppointmentStatus.CANCELLED: set(),
    }

    @staticmethod
    def create_appointment(user, validated_data: dict):
        validated_data["user"] = user
        return AppointmentRepository.create_appointment(validated_data)

    @staticmethod
    def update_status(user, appointment_id: int, new_status: str):
        appointment = AppointmentRepository.get_by_id(appointment_id)

        if appointment.user_id == user.id:
            if new_status != AppointmentStatus.CANCELLED:
                raise PermissionDenied("Requester can only cancel their own appointment.")
            if appointment.status not in AppointmentService.REQUESTER_CANCELABLE_STATUSES:
                raise ValidationError("This appointment cannot be cancelled anymore.")
        elif appointment.property.owner_id == user.id or getattr(user, "is_staff", False):
            allowed_statuses = AppointmentService.OWNER_ALLOWED_TRANSITIONS.get(appointment.status, set())
            if new_status not in allowed_statuses:
                raise ValidationError("Invalid status transition for owner/admin.")
        else:
            raise PermissionDenied("You do not have permission to update this appointment.")

        appointment.status = new_status
        appointment.save(update_fields=["status", "updated_at"])
        return appointment

    @staticmethod
    def cancel_appointment(user, appointment_id: int):
        return AppointmentService.update_status(user, appointment_id, AppointmentStatus.CANCELLED)
