import pytest
from unittest.mock import MagicMock, patch

from app.services.eta_service import EtaCalculator


class TestEtaCalculator:
    def test_compute_eta_returns_required_fields(self):
        mock_route = MagicMock()
        mock_route.get_best_route.return_value = {
            "provider": "osrm",
            "distance_meters": 2845,
            "duration_seconds": 510,
            "geometry": [{"lat": 19.9975, "lng": 73.7898}],
        }

        calc = EtaCalculator(route_service=mock_route)
        result = calc.compute_eta(
            device_id="pilgrim_001",
            current_lat=19.9975,
            current_lng=73.7898,
            dest_lat=19.9956,
            dest_lng=73.7810,
        )

        assert "route_distance_meters" in result
        assert "travel_time_seconds" in result
        assert "remaining_distance_meters" in result
        assert "eta" in result
        assert "route_updated" in result

    def test_route_updated_on_first_call(self):
        mock_route = MagicMock()
        mock_route.get_best_route.return_value = {
            "provider": "osrm",
            "distance_meters": 1000,
            "duration_seconds": 120,
            "geometry": [],
        }

        calc = EtaCalculator(route_service=mock_route)
        result = calc.compute_eta(
            device_id="pilgrim_001",
            current_lat=19.9975,
            current_lng=73.7898,
            dest_lat=19.9956,
            dest_lng=73.7810,
        )

        assert result["route_updated"] is True

    def test_force_recalculate_sets_route_updated(self):
        mock_route = MagicMock()
        mock_route.get_best_route.return_value = {
            "provider": "osrm",
            "distance_meters": 1000,
            "duration_seconds": 120,
            "geometry": [],
        }

        calc = EtaCalculator(route_service=mock_route)
        result = calc.compute_eta(
            device_id="pilgrim_001",
            current_lat=19.9975,
            current_lng=73.7898,
            dest_lat=19.9956,
            dest_lng=73.7810,
            force_recalculate=True,
        )

        assert result["route_updated"] is True

    def test_no_route_service_raises(self):
        calc = EtaCalculator(route_service=None)
        with pytest.raises(RuntimeError, match="No routing service"):
            calc.compute_eta(
                device_id="pilgrim_001",
                current_lat=19.9975,
                current_lng=73.7898,
                dest_lat=19.9956,
                dest_lng=73.7810,
            )
