from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Appointment
from .repositories import AppointmentRepository
from .serializers import AppointmentSerializer, AppointmentStatusUpdateSerializer
from .services import AppointmentService


class AppointmentListView(generics.ListCreateAPIView):
    """
    GET: appointments created by current requester.
    POST: create a new appointment request.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return AppointmentRepository.get_user_appointments(self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = AppointmentService.create_appointment(
            user=request.user,
            validated_data=serializer.validated_data,
        )
        return Response(
            AppointmentSerializer(appointment, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )


class OwnerAppointmentListView(generics.ListAPIView):
    """
    GET: appointments on properties owned by current user.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return AppointmentRepository.get_owner_appointments(self.request.user)


class AppointmentDetailView(generics.RetrieveDestroyAPIView):
    """
    GET: appointment details for requester/owner/admin.
    DELETE: requester can cancel appointment.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Appointment.objects.none()
        if not self.request.user.is_authenticated:
            return Appointment.objects.none()
        return AppointmentRepository.get_actor_scope(self.request.user)

    def delete(self, request, *args, **kwargs):
        AppointmentService.cancel_appointment(request.user, self.kwargs["pk"])
        return Response({"message": "Appointment cancelled successfully."}, status=status.HTTP_200_OK)


class AppointmentStatusUpdateView(APIView):
    """
    PATCH: update appointment status.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        serializer = AppointmentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment = AppointmentService.update_status(
            user=request.user,
            appointment_id=pk,
            new_status=serializer.validated_data["status"],
        )

        return Response(
            {
                "message": "Appointment status updated.",
                "data": AppointmentSerializer(appointment).data,
            },
            status=status.HTTP_200_OK,
        )
