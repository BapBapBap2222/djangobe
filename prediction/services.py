import os
import joblib
import pandas as pd
from django.conf import settings


class PredictionService:
    """Service Layer for Vietnam house price prediction."""

    _model_pipeline = None

    @classmethod
    def get_model(cls):
        """Lazy-load machine learning model."""
        if cls._model_pipeline is None:
            model_dir = os.path.join(
                settings.BASE_DIR.parent,
                "LinearRegressionModel",
                "models",
            )
            model_path = os.path.join(model_dir, "vietname.pkl")
            fallback_path = os.path.join(model_dir, "lr_pipeline.joblib")
            if not os.path.exists(model_path) and os.path.exists(fallback_path):
                model_path = fallback_path
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    "Machine learning model file not found. Expected 'vietname.pkl'."
                )
            cls._model_pipeline = joblib.load(model_path)
        return cls._model_pipeline

    @staticmethod
    def predict_price(data: dict) -> dict:
        """
        Takes raw input dict, processes it, and returns the prediction result dict.
        Raises ValueError or FileNotFoundError if validation or model loading fails.
        """
        # 1. Extract and normalize variables from vietnam-real-estates schema.
        try:
            province_name = str(data.get("province_name", "Hà Nội")).strip() or "Hà Nội"
            property_type_name = str(data.get("property_type_name", "Nhà")).strip() or "Nhà"
            area = float(data.get("area", 80.0))
            floor_count = float(data.get("floor_count", 3.0))
            bedroom_count = float(data.get("bedroom_count", 3.0))
            bathroom_count = float(data.get("bathroom_count", 2.0))
        except (TypeError, ValueError):
            raise ValueError("Invalid numerical values provided in the payload.")

        if area <= 0:
            raise ValueError("Field 'area' must be greater than 0.")
        if floor_count < 0 or bedroom_count < 0 or bathroom_count < 0:
            raise ValueError("floor_count, bedroom_count, bathroom_count must be >= 0.")

        # 2. Create DataFrame in the exact schema expected by the current model.
        input_data = pd.DataFrame([{
            "property_type_name": property_type_name,
            "province_name": province_name,
            "area": area,
            "floor_count": floor_count,
            "bedroom_count": bedroom_count,
            "bathroom_count": bathroom_count,
        }])

        # 3. Load model and predict.
        pipeline = PredictionService.get_model()
        predicted_price_vnd = float(pipeline.predict(input_data)[0])
        if predicted_price_vnd <= 0:
            predicted_price_vnd = 100_000_000.0

        # 4. Construct business response.
        price_min = predicted_price_vnd * 0.88
        price_max = predicted_price_vnd * 1.12
        price_per_m2 = predicted_price_vnd / area
        confidence = 0.80

        return {
            "estimated_price": round(predicted_price_vnd),
            "price_min": round(price_min),
            "price_max": round(price_max),
            "confidence": confidence,
            "price_per_m2": round(price_per_m2),
        }
