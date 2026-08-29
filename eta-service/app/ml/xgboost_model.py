import os
import logging
from typing import Optional, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger("eta-service.ml")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("XGBoost library not installed. Falling back to heuristic ML estimator.")


class XGBoostEtaPredictor:
    """
    XGBoost-backed machine learning model for predicting travel delays
    and temple/darshan queue waiting times for pilgrimage routes.
    """

    def __init__(
        self,
        eta_model_path: Optional[str] = None,
        queue_model_path: Optional[str] = None,
    ):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.eta_model_path = eta_model_path or os.path.join(base_dir, "artifacts", "xgb_eta_model.json")
        self.queue_model_path = queue_model_path or os.path.join(base_dir, "artifacts", "xgb_queue_model.json")

        self.eta_model = None
        self.queue_model = None
        self.is_eta_model_loaded = False
        self.is_queue_model_loaded = False

        self._load_models()

    def _load_models(self) -> None:
        """Attempt to load XGBoost JSON model artifacts from disk."""
        if not XGBOOST_AVAILABLE:
            return

        if os.path.exists(self.eta_model_path):
            try:
                model = xgb.XGBRegressor()
                model.load_model(self.eta_model_path)
                self.eta_model = model
                self.is_eta_model_loaded = True
                logger.info(f"Loaded XGBoost ETA model from {self.eta_model_path}")
            except Exception as e:
                logger.error(f"Failed to load XGBoost ETA model: {e}")

        if os.path.exists(self.queue_model_path):
            try:
                model = xgb.XGBRegressor()
                model.load_model(self.queue_model_path)
                self.queue_model = model
                self.is_queue_model_loaded = True
                logger.info(f"Loaded XGBoost Queue model from {self.queue_model_path}")
            except Exception as e:
                logger.error(f"Failed to load XGBoost Queue model: {e}")

    @staticmethod
    def extract_travel_features(
        distance_meters: float,
        base_duration_seconds: float,
        hour_of_day: int = 12,
        day_of_week: int = 0,
        crowd_density_index: float = 0.2,
        is_festival: bool = False,
        weather_severity: float = 0.0,
        traffic_density: float = 0.0,
        road_closure: bool = False,
        accident_reported: bool = False,
        holiday: bool = False,
    ) -> np.ndarray:
        """
        Extract numerical feature matrix for travel duration prediction.
        Features (11): [distance_meters, base_duration_seconds, hour_of_day, day_of_week, crowd_density_index, is_festival, weather_severity, traffic_density, road_closure, accident_reported, holiday]
        """
        return np.array(
            [[
                float(distance_meters),
                float(base_duration_seconds),
                float(hour_of_day),
                float(day_of_week),
                float(crowd_density_index),
                1.0 if is_festival else 0.0,
                float(weather_severity),
                float(traffic_density),
                1.0 if road_closure else 0.0,
                1.0 if accident_reported else 0.0,
                1.0 if holiday else 0.0,
            ]],
            dtype=np.float32,
        )

    @staticmethod
    def extract_queue_features(
        arrival_hour: int = 12,
        day_of_week: int = 0,
        crowd_density_index: float = 0.2,
        is_festival: bool = False,
        weather_severity: float = 0.0,
        traffic_density: float = 0.0,
        holiday: bool = False,
    ) -> np.ndarray:
        """
        Extract feature matrix for temple queue waiting time prediction.
        Features (7): [arrival_hour, day_of_week, crowd_density_index, is_festival, weather_severity, traffic_density, holiday]
        """
        return np.array(
            [[
                float(arrival_hour),
                float(day_of_week),
                float(crowd_density_index),
                1.0 if is_festival else 0.0,
                float(weather_severity),
                float(traffic_density),
                1.0 if holiday else 0.0,
            ]],
            dtype=np.float32,
        )

    def predict_travel_time(
        self,
        distance_meters: float,
        base_duration_seconds: float,
        hour_of_day: int = 12,
        day_of_week: int = 0,
        crowd_density_index: float = 0.2,
        is_festival: bool = False,
        weather_severity: float = 0.0,
        traffic_density: float = 0.0,
        road_closure: bool = False,
        accident_reported: bool = False,
        holiday: bool = False,
    ) -> Tuple[float, bool]:
        """
        Predict travel duration in seconds.
        Returns: (predicted_duration_seconds, ml_model_used)
        """
        if self.is_eta_model_loaded and self.eta_model is not None:
            features = self.extract_travel_features(
                distance_meters=distance_meters,
                base_duration_seconds=base_duration_seconds,
                hour_of_day=hour_of_day,
                day_of_week=day_of_week,
                crowd_density_index=crowd_density_index,
                is_festival=is_festival,
                weather_severity=weather_severity,
                traffic_density=traffic_density,
                road_closure=road_closure,
                accident_reported=accident_reported,
                holiday=holiday,
            )
            prediction = float(self.eta_model.predict(features)[0])
            # Scale prediction delay ratio relative to baseline duration
            raw_training_baseline = max(1.0, float(base_duration_seconds) if float(base_duration_seconds) < 300.0 else 160.0)
            delay_factor = max(1.0, prediction / raw_training_baseline)
            predicted_seconds = max(base_duration_seconds, base_duration_seconds * delay_factor)
            return round(predicted_seconds, 1), True

        # Dynamic heuristic fallback when model artifact is missing
        delay_multiplier = 1.0 + (crowd_density_index * 0.6) + (traffic_density * 0.5) + (0.4 if is_festival else 0.0) + (weather_severity * 0.35)
        if road_closure:
            delay_multiplier += 0.8
        if accident_reported:
            delay_multiplier += 0.4
        if holiday:
            delay_multiplier += 0.2
        # Add slight peak-hour multiplier (between 8 AM and 8 PM)
        if 8 <= hour_of_day <= 20:
            delay_multiplier += 0.15
        
        fallback_seconds = base_duration_seconds * delay_multiplier
        return round(fallback_seconds, 1), False

    def predict_queue_time(
        self,
        arrival_hour: int = 12,
        day_of_week: int = 0,
        crowd_density_index: float = 0.2,
        is_festival: bool = False,
        weather_severity: float = 0.0,
        traffic_density: float = 0.0,
        holiday: bool = False,
    ) -> Tuple[float, bool]:
        """
        Predict temple queue waiting duration in seconds.
        Returns: (predicted_queue_seconds, ml_model_used)
        """
        if self.is_queue_model_loaded and self.queue_model is not None:
            features = self.extract_queue_features(
                arrival_hour=arrival_hour,
                day_of_week=day_of_week,
                crowd_density_index=crowd_density_index,
                is_festival=is_festival,
                weather_severity=weather_severity,
                traffic_density=traffic_density,
                holiday=holiday,
            )
            prediction = float(self.queue_model.predict(features)[0])
            return round(max(0.0, prediction), 1), True

        # Heuristic fallback for darshan queue prediction
        # Base queue: 0 to 30 mins depending on density + festival spike
        base_queue_minutes = crowd_density_index * 30.0
        if is_festival:
            base_queue_minutes += 45.0
        if holiday or day_of_week in (5, 6):  # Weekend/Holiday
            base_queue_minutes += 15.0

        fallback_seconds = base_queue_minutes * 60.0
        return round(fallback_seconds, 1), False
