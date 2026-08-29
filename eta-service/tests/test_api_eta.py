import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestEtaEndpoint:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_eta_endpoint_requires_device_id(self):
        response = client.post(
            "/api/v1/eta",
            json={
                "timestamp": "2026-08-05T09:15:00Z",
                "current_location": {"lat": 19.9975, "lng": 73.7898},
                "destination": {"lat": 19.9956, "lng": 73.7810},
            },
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_eta_endpoint_requires_current_location(self):
        response = client.post(
            "/api/v1/eta",
            json={
                "device_id": "pilgrim_001",
                "timestamp": "2026-08-05T09:15:00Z",
                "destination": {"lat": 19.9956, "lng": 73.7810},
            },
        )
        assert response.status_code == 422

    def test_eta_endpoint_requires_destination(self):
        response = client.post(
            "/api/v1/eta",
            json={
                "device_id": "pilgrim_001",
                "timestamp": "2026-08-05T09:15:00Z",
                "current_location": {"lat": 19.9975, "lng": 73.7898},
            },
        )
        assert response.status_code == 422

    def test_eta_endpoint_invalid_timestamp(self):
        response = client.post(
            "/api/v1/eta",
            json={
                "device_id": "pilgrim_001",
                "timestamp": "not-a-timestamp",
                "current_location": {"lat": 19.9975, "lng": 73.7898},
                "destination": {"lat": 19.9956, "lng": 73.7810},
            },
        )
        assert response.status_code == 422

    def test_eta_endpoint_invalid_latitude(self):
        response = client.post(
            "/api/v1/eta",
            json={
                "device_id": "pilgrim_001",
                "timestamp": "2026-08-05T09:15:00Z",
                "current_location": {"lat": 95.0, "lng": 73.7898},
                "destination": {"lat": 19.9956, "lng": 73.7810},
            },
        )
        assert response.status_code == 422

    def test_eta_endpoint_invalid_longitude(self):
        response = client.post(
            "/api/v1/eta",
            json={
                "device_id": "pilgrim_001",
                "timestamp": "2026-08-05T09:15:00Z",
                "current_location": {"lat": 19.9975, "lng": 200.0},
                "destination": {"lat": 19.9956, "lng": 73.7810},
            },
        )
        assert response.status_code == 422

    def test_eta_endpoint_valid_coordinates_custom_schema(self):
        response = client.post(
            "/api/v1/eta",
            json={
                "device_id": "pilgrim_test_coords",
                "timestamp": "2026-08-29T09:45:00Z",
                "current_location": {"lat": 20.00841, "lng": 73.75573},
                "destination": {"lat": 19.99814, "lng": 73.76912},
                "crowd_density_index": 0.5,
                "is_festival": False,
                "weather_severity": 0.1,
                "traffic_density": 0.3,
                "include_queue_time": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["device_id"] == "pilgrim_test_coords"
        assert data["route_distance_meters"] > 0
        assert "travel_time_seconds" in data
        assert "eta" in data

