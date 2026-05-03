from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from appointments.models import AppointmentStatus
from utils.factories import TestDataFactory


class AppointmentApiTests(APITestCase):
    def setUp(self):
        self.owner = TestDataFactory.create_user()
        self.requester = TestDataFactory.create_user()
        self.other_user = TestDataFactory.create_user()
        self.admin = TestDataFactory.create_user(is_staff=True)
        self.property_obj = TestDataFactory.create_property(owner=self.owner)

    def _create_payload(self, *, day_offset=1, time_value="10:00:00"):
        return {
            "property": self.property_obj.id,
            "date": str(date.today() + timedelta(days=day_offset)),
            "time": time_value,
            "name": "Le Van A",
            "phone": "0900000000",
            "message": "Hen xem nha",
        }

    def test_user_can_create_appointment(self):
        self.client.force_authenticate(user=self.requester)
        response = self.client.post(
            reverse("appointment-list"),
            self._create_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], AppointmentStatus.PENDING)

    def test_user_cannot_book_own_property(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            reverse("appointment-list"),
            self._create_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("property", response.data)

    def test_user_cannot_create_appointment_in_past(self):
        self.client.force_authenticate(user=self.requester)
        response = self.client.post(
            reverse("appointment-list"),
            self._create_payload(day_offset=-1),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("date" in response.data or "time" in response.data)

    def test_owner_can_confirm_pending_appointment(self):
        appointment = TestDataFactory.create_appointment(
            user=self.requester,
            property_obj=self.property_obj,
            status=AppointmentStatus.PENDING,
        )
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            reverse("appointment-status-update", kwargs={"pk": appointment.id}),
            {"status": AppointmentStatus.CONFIRMED},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["status"], AppointmentStatus.CONFIRMED)

    def test_owner_cannot_complete_pending_appointment_directly(self):
        appointment = TestDataFactory.create_appointment(
            user=self.requester,
            property_obj=self.property_obj,
            status=AppointmentStatus.PENDING,
        )
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            reverse("appointment-status-update", kwargs={"pk": appointment.id}),
            {"status": AppointmentStatus.COMPLETED},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_requester_can_cancel_pending_appointment(self):
        appointment = TestDataFactory.create_appointment(
            user=self.requester,
            property_obj=self.property_obj,
            status=AppointmentStatus.PENDING,
        )
        self.client.force_authenticate(user=self.requester)
        response = self.client.patch(
            reverse("appointment-status-update", kwargs={"pk": appointment.id}),
            {"status": AppointmentStatus.CANCELLED},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["status"], AppointmentStatus.CANCELLED)

    def test_requester_cannot_confirm_appointment(self):
        appointment = TestDataFactory.create_appointment(
            user=self.requester,
            property_obj=self.property_obj,
            status=AppointmentStatus.PENDING,
        )
        self.client.force_authenticate(user=self.requester)
        response = self.client.patch(
            reverse("appointment-status-update", kwargs={"pk": appointment.id}),
            {"status": AppointmentStatus.CONFIRMED},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_requester_can_cancel_via_delete_endpoint(self):
        appointment = TestDataFactory.create_appointment(
            user=self.requester,
            property_obj=self.property_obj,
            status=AppointmentStatus.PENDING,
        )
        self.client.force_authenticate(user=self.requester)
        response = self.client.delete(reverse("appointment-detail", kwargs={"pk": appointment.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_requester_cannot_cancel_completed_appointment(self):
        appointment = TestDataFactory.create_appointment(
            user=self.requester,
            property_obj=self.property_obj,
            status=AppointmentStatus.COMPLETED,
        )
        self.client.force_authenticate(user=self.requester)
        response = self.client.delete(reverse("appointment-detail", kwargs={"pk": appointment.id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unrelated_user_cannot_view_appointment_detail(self):
        appointment = TestDataFactory.create_appointment(
            user=self.requester,
            property_obj=self.property_obj,
        )
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(reverse("appointment-detail", kwargs={"pk": appointment.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_list_owner_appointments(self):
        TestDataFactory.create_appointment(user=self.requester, property_obj=self.property_obj)
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(reverse("owner-appointment-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_staff_can_confirm_any_appointment(self):
        appointment = TestDataFactory.create_appointment(
            user=self.requester,
            property_obj=self.property_obj,
            status=AppointmentStatus.PENDING,
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse("appointment-status-update", kwargs={"pk": appointment.id}),
            {"status": AppointmentStatus.CONFIRMED},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["status"], AppointmentStatus.CONFIRMED)
