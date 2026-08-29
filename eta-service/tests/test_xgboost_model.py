import pytest
from app.ml.xgboost_model import XGBoostEtaPredictor
from app.services.eta_service import EtaCalculator
from app.models.request import EtaRequest
from app.models.response import EtaResponse


def test_xgboost_feature_extraction():
    """Test feature matrix shapes for travel and queue features."""
    travel_features = XGBoostEtaPredictor.extract_travel_features(
        distance_meters=1000.0,
        base_duration_seconds=120.0,
        hour_of_day=14,
        day_of_week=2,
        crowd_density_index=0.5,
        is_festival=True,
        weather_severity=0.1,
        traffic_density=0.3,
        road_closure=False,
        accident_reported=False,
        holiday=True,
    )
    assert travel_features.shape == (1, 11)
    assert travel_features[0, 0] == 1000.0
    assert travel_features[0, 5] == 1.0  # is_festival
    assert travel_features[0, 10] == 1.0  # holiday

    queue_features = XGBoostEtaPredictor.extract_queue_features(
        arrival_hour=10,
        day_of_week=0,
        crowd_density_index=0.8,
        is_festival=False,
        weather_severity=0.2,
        traffic_density=0.5,
        holiday=False,
    )
    assert queue_features.shape == (1, 7)


def test_xgboost_fallback_predictions():
    """Test predictor returns fallback calculations when model files are not yet loaded."""
    predictor = XGBoostEtaPredictor(eta_model_path="non_existent.json", queue_model_path="non_existent.json")
    assert not predictor.is_eta_model_loaded
    assert not predictor.is_queue_model_loaded

    travel_sec, used = predictor.predict_travel_time(
        distance_meters=2000.0,
        base_duration_seconds=200.0,
        hour_of_day=12,
        day_of_week=1,
        crowd_density_index=0.5,
        is_festival=True,
    )
    assert not used
    assert travel_sec > 200.0  # Should apply delay multiplier

    queue_sec, q_used = predictor.predict_queue_time(
        arrival_hour=10,
        day_of_week=0,
        crowd_density_index=0.5,
        is_festival=True,
    )
    assert not q_used
    assert queue_sec > 0.0


def test_eta_calculator_with_ml():
    """Test EtaCalculator integrates ML prediction outputs correctly."""
    class DummyRouteService:
        def get_best_route(self, current_lat, current_lng, dest_lat, dest_lng, waypoints=None):
            return {
                "distance_meters": 1500.0,
                "duration_seconds": 300.0,
                "geometry": "dummy_geometry",
            }

    predictor = XGBoostEtaPredictor(eta_model_path="non_existent.json", queue_model_path="non_existent.json")
    calculator = EtaCalculator(route_service=DummyRouteService(), ml_predictor=predictor)

    res = calculator.compute_eta(
        device_id="test_dev_01",
        current_lat=19.9975,
        current_lng=73.7898,
        dest_lat=19.9956,
        dest_lng=73.7810,
        crowd_density_index=0.6,
        is_festival=True,
    )

    assert res["route_distance_meters"] == 1500.0
    assert res["base_travel_time_seconds"] == 300.0
    assert res["predicted_travel_time_seconds"] > 300.0
    assert res["predicted_queue_time_seconds"] > 0.0
    assert res["travel_time_seconds"] == res["predicted_travel_time_seconds"] + res["predicted_queue_time_seconds"]
    assert res["traffic_delay_factor"] > 1.0
