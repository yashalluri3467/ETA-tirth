import pytest
from unittest.mock import MagicMock

from app.services.session_service import SessionManager


class TestSessionManager:
    def test_create_session_returns_dict(self):
        calc = SessionManager()
        session = calc.create_or_update_session(
            device_id="pilgrim_001",
            origin_lat=19.9975,
            origin_lng=73.7898,
            dest_lat=19.9956,
            dest_lng=73.7810,
            route_distance_meters=2845,
            route_geometry=[{"lat": 19.9975, "lng": 73.7898}],
        )

        assert session["device_id"] == "pilgrim_001"
        assert session["origin"]["lat"] == 19.9975
        assert session["destination"]["lat"] == 19.9956
        assert session["route_distance_meters"] == 2845

    def test_has_deviated_no_geometry(self):
        calc = SessionManager()
        session = {"route_geometry": []}
        assert calc.has_deviated(session, 19.9975, 73.7898) is False

    def test_has_not_deviated_near_route(self):
        calc = SessionManager()
        session = {
            "route_geometry": [
                {"lat": 19.9975, "lng": 73.7898},
                {"lat": 19.9960, "lng": 73.7850},
            ]
        }
        # User is very close to the first point on the route
        assert calc.has_deviated(session, 19.9975, 73.7898, threshold_meters=50) is False

    def test_distance_from_origin(self):
        calc = SessionManager()
        session = {
            "origin": {"lat": 19.9975, "lng": 73.7898},
        }
        dist = calc.distance_from_origin(session, 19.9975, 73.7898)
        assert dist == 0.0

    def test_clear_session_with_no_cache(self):
        calc = SessionManager()
        calc.clear_session("pilgrim_001")  # Should not raise
