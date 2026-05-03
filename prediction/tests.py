from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class PricePredictionApiTests(APITestCase):
    @patch("prediction.views.PredictionService.predict_price")
    def test_prediction_success_with_valid_payload(self, mock_predict):
        mock_predict.return_value = {
            "estimated_price": 1000000000,
            "price_min": 900000000,
            "price_max": 1100000000,
            "confidence": 0.82,
            "price_per_m2": 12500000,
        }
        payload = {
            "province_name": "Hà Nội",
            "district_name": "Cầu Giấy",
            "ward_name": "Dịch Vọng",
            "property_type_name": "Nhà",
            "area": 80,
            "floor_count": 4,
            "bedroom_count": 3,
            "bathroom_count": 3,
        }
        response = self.client.post(reverse("price-prediction"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("estimated_price", response.data)
        mock_predict.assert_called_once()

    @patch("prediction.views.PredictionService.predict_price")
    def test_prediction_rejects_invalid_payload(self, mock_predict):
        payload = {"area": 0, "property_type_name": "UNKNOWN"}
        response = self.client.post(reverse("price-prediction"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        mock_predict.assert_not_called()

    @patch("prediction.views.PredictionService.predict_price")
    def test_prediction_hides_internal_error_details(self, mock_predict):
        mock_predict.side_effect = FileNotFoundError(
            "Machine learning model file not found at /secret/models/vietname.pkl"
        )
        payload = {
            "province_name": "Ha Noi",
            "property_type_name": "Nhà",
            "area": 80,
            "floor_count": 4,
            "bedroom_count": 3,
            "bathroom_count": 3,
        }
        response = self.client.post(reverse("price-prediction"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data.get("error"), "Internal server error.")
        self.assertNotIn("secret", str(response.data))
