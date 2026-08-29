import pytest
from pydantic import ValidationError
from app.models.request import EtaRequest, Location


class TestLocation:
    def test_valid_location(self):
        loc = Location(lat=19.9975, lng=73.7898)
        assert loc.lat == 19.9975
        assert loc.lng == 73.7898

    def test_location_missing_lat(self):
        with pytest.raises(ValidationError):
            Location(lng=73.7898)

    def test_location_missing_lng(self):
        with pytest.raises(ValidationError):
            Location(lat=19.9975)

    def test_location_lat_out_of_range(self):
        with pytest.raises(ValidationError):
            Location(lat=91.0, lng=0.0)

    def test_location_lng_out_of_range(self):
        with pytest.raises(ValidationError):
            Location(lat=0.0, lng=181.0)


class TestEtaRequest:
    def test_valid_request(self):
        req = EtaRequest(
            device_id="pilgrim_001",
            timestamp="2026-08-05T09:15:00Z",
            current_location={"lat": 19.9975, "lng": 73.7898},
            destination={"lat": 19.9956, "lng": 73.7810},
        )
        assert req.device_id == "pilgrim_001"

    def test_missing_device_id(self):
        with pytest.raises(ValidationError):
            EtaRequest(
                timestamp="2026-08-05T09:15:00Z",
                current_location={"lat": 19.9975, "lng": 73.7898},
                destination={"lat": 19.9956, "lng": 73.7810},
            )

    def test_missing_timestamp(self):
        with pytest.raises(ValidationError):
            EtaRequest(
                device_id="pilgrim_001",
                current_location={"lat": 19.9975, "lng": 73.7898},
                destination={"lat": 19.9956, "lng": 73.7810},
            )

    def test_invalid_timestamp_format(self):
        with pytest.raises(ValidationError):
            EtaRequest(
                device_id="pilgrim_001",
                timestamp="2026/08/05 09:15:00",
                current_location={"lat": 19.9975, "lng": 73.7898},
                destination={"lat": 19.9956, "lng": 73.7810},
            )
